import networkx as nx
import pickle
import os
from time import time
from datetime import datetime
from uuid import uuid4


def roam(graph, target, budget=1):
    """
    Remove one, add many until target has degree 1 (extreme case)
    Input:
        graph: to be updated by roam_protector and return
        target: the node to hide
        budget: the number of edges to add between removed neighbor and the rest of neighbors
        NOTE: budget here is the fixed rewiring budget.
    Return: the graph
    """
    target_neighbors = [(node, graph.degree(node)) for node in graph[target]]
    neighbors_sorted = sorted(target_neighbors, key=lambda x: x[1], reverse=False)
    # if len(neighbors_sorted) == 0:
    #     return graph,0
    v0 = neighbors_sorted.pop(-1)[0]
    v0_neighbors = graph[v0]
    neighbors_sorted = [i[0] for i in neighbors_sorted if i[0] not in v0_neighbors]
    graph.remove_edge(target, v0)
    to_add = [(v0, i) for i in neighbors_sorted[:budget]]
    graph.add_edges_from(to_add)
    spent = 1 + len(to_add)
    return graph, spent


def run_roam(graph, subg, target, budgets):
    result = {}
    for idx in budgets:
        s = time()
        budget = idx * graph.number_of_edges()
        community = subg.copy()
        G = graph.copy()
        actions = {"rem": 0, "add": 0}
        stop = False
        while sum(actions.values()) <= budget and not stop:
            # roam
            spent = 1
            while community.degree(target) > 1 and spent > 0:
                G, spent = roam(G, target, budget=1)
                removed = [(target, n) for n in community[target] if n not in G[target]]
                added = [e for e in G.edges() if e[0] in community and 
                         e[1] in community and e not in community.edges()]

                community.add_edges_from(added)
                community.remove_edges_from(removed)
                actions["rem"] += 1
                actions["add"] += spent - 1
                if sum(actions.values()) >= budget:
                    break

            stop = True

        e = time() - s
        result[idx] = {
            "graph": G.copy(),
            "community": community.copy(),
            "num_del_edges": actions["rem"],
            "num_add_edges": actions["add"],
            "dtime": e,
        }
        print(f"\t budget {idx} done! Elapsed: {e}")
    return result


def update_sorted_edges(sorted_edges, changed_edges, sorted_edge_names):
    for edge in changed_edges:
        idx = sorted_edge_names.index(edge)
        sorted_edges[idx][1] -= 1
        # stop = False
        if idx == len(sorted_edges) - 1:
            return sorted_edges, sorted_edge_names
        if sorted_edges[idx][1] < sorted_edges[idx + 1][1]:
            # while not stop:
            tmp = sorted(sorted_edges[idx:], key=lambda x: x[1], reverse=True)
            sorted_edges[idx:] = tmp
            sorted_edge_names[idx:] = [i[0] for i in sorted_edges[idx:]]
            # if sorted_edges[idx][1] >= sorted_edges[idx+1][1]:
            #     stop = True
    return sorted_edges, sorted_edge_names


def run_greedy(graph, subg, target, budgets):
    # pass
    result = {}
    # one time full computation, for next rounds (different budgets) we load the result of the previous round
    edges_score = {e: graph.degree(e[0]) + graph.degree(e[1]) for e in graph.edges()}
    sorted_edges = sorted(
        [[i[0], i[1]] for i in edges_score.items()], key=lambda x: x[1], reverse=True
    )
    sorted_edge_names = [i[0] for i in sorted_edges]
    save2 = "./tmp"
    if not os.path.exists(save2):
        os.makedirs(save2)
    eventid = datetime.now().strftime("%Y%m%d-%H%M%S-") + str(uuid4()) + ".pkl"
    path = os.path.join(save2, eventid)
    with open(path, "wb") as f:
        pickle.dump(
            dict(
                graph=graph,
                sorted_edges=sorted_edges,
                sorted_edge_names=sorted_edge_names,
                used_budget=0,
            ),
            f,
        )
    count = 0
    for idx in budgets:
        count += 1
        s = time()
        with open(path, "rb") as f:
            rtrv = pickle.load(
                f
            )  # retrieved materials from the last budget to speed up computation
        sorted_edges = rtrv["sorted_edges"]
        sorted_edge_names = rtrv["sorted_edge_names"]
        used_budget = rtrv["used_budget"]
        budget = idx * graph.number_of_edges()
        G = rtrv["graph"]

        # once in  while resort to compensate for possible estimate sorting
        if count % 5 == 0:
            edges_score = {e: G.degree(e[0]) + G.degree(e[1]) for e in G.edges()}
            sorted_edges = sorted(
                [[i[0], i[1]] for i in edges_score.items()],
                key=lambda x: x[1],
                reverse=True,
            )
            sorted_edge_names = [i[0] for i in sorted_edges]

        stop = False if budget - used_budget > 0 else True
        deleted = []
        while not stop:
            candidate = sorted_edges[0][0]
            changed_edges = [
                (node, neigh) if (node, neigh) in edges_score else (neigh, node)
                for node in candidate
                for neigh in G[node]
                if neigh not in candidate
            ]
            sorted_edges, sorted_edge_names = update_sorted_edges(
                sorted_edges, changed_edges, sorted_edge_names
            )
            deleted.append(candidate)
            if len(deleted) >= budget - used_budget:
                stop = True

        G.remove_edges_from(deleted)
        used_budget += len(deleted)
        # save the result of this budget to be used for the next budget and save time!
        with open(path, "wb") as f:
            pickle.dump(
                dict(
                    graph=G,
                    sorted_edges=sorted_edges,
                    sorted_edge_names=sorted_edge_names,
                    used_budget=used_budget,
                ),
                f,
            )

        e = time() - s
        result[idx] = {
            "graph": G.copy(),
            "community": None,
            "num_del_edges": used_budget,
            "num_add_edges": 0,
            "dtime": e,
        }
        print(f"\t budget {idx} done! Elapsed: {e}")
    return result


def run_maxdeg(graph, subg, target, budgets):
    result = {}
    edges_score = {e: graph.degree(e[0]) + graph.degree(e[1]) for e in graph.edges()}
    sorted_edges = sorted(
        [[i[0], i[1]] for i in edges_score.items()], key=lambda x: x[1], reverse=True
    )
    sorted_edge_names = [i[0] for i in sorted_edges]
    for idx in budgets:
        s = time()
        budget = idx * graph.number_of_edges()
        spent = 0
        G = graph.copy()
        for e in sorted_edge_names:
            G.remove_edges_from([e])
            if not nx.is_connected(G):
                G.add_edges_from([e])
                continue
            spent += 1
            if spent >= budget:
                break
        e = time() - s
        result[idx] = {
            "graph": G.copy(),
            "community": None,
            "num_del_edges": spent,
            "num_add_edges": 0,
            "dtime": e,
        }
        print(f"\t budget {idx} done! Elapsed: {e}")
    return result


def run_betweenness(graph, subg, target, budgets):
    result = {}
    nodes = [i for i in graph.nodes() if graph.degree(i) > 1]
    if len(nodes) <= int(0.001 * graph.number_of_edges()):
        # print('calculating subset of length ',len(nodes))
        escores = sorted(
            nx.edge_betweenness_centrality_subset(
                graph, sources=nodes, targets=nodes
            ).items(),
            key=lambda x: x[1],
            reverse=True,
        )
    else:
        escores = sorted(
            nx.edge_betweenness_centrality(
                graph, k=int(0.001 * graph.number_of_edges())
            ).items(),
            key=lambda x: x[1],
            reverse=True,
        )

    sorted_edge_names = [i[0] for i in escores]
    for idx in budgets:
        s = time()
        budget = idx * graph.number_of_edges()
        spent = 0
        G = graph.copy()
        for e in sorted_edge_names:
            G.remove_edges_from([e])
            if not nx.is_connected(G):
                G.add_edges_from([e])
                continue
            spent += 1
            if spent >= budget:
                break
        e = time() - s
        result[idx] = {
            "graph": G.copy(),
            "community": None,
            "num_del_edges": spent,
            "num_add_edges": 0,
            "dtime": e,
        }
        print(f"\t budget {idx} done! Elapsed: {e}")
    return result


def run_pagerank(graph, subg, target, budgets):
    result = {}
    nscores = nx.pagerank(graph)
    escores = sorted(
        [(edge, nscores[edge[0]] + nscores[edge[1]]) for edge in graph.edges()],
        key=lambda x: x[1],
        reverse=True,
    )
    sorted_edge_names = [i[0] for i in escores]
    for idx in budgets:
        s = time()
        budget = idx * graph.number_of_edges()
        spent = 0
        G = graph.copy()
        for e in sorted_edge_names:
            G.remove_edges_from([e])
            if not nx.is_connected(G):
                G.add_edges_from([e])
                continue
            spent += 1
            if spent >= budget:
                break
        e = time() - s
        result[idx] = {
            "graph": G.copy(),
            "community": None,
            "num_del_edges": spent,
            "num_add_edges": 0,
            "dtime": e,
        }
        print(f"\t budget {idx} done! Elapsed: {e}")
    return result
