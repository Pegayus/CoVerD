import numpy as np
import pickle
import os
from time import time
from scipy import stats
from community import best_partition


def get_comscore(graph, coms):
    """
    Get community-based scores
    Input:
        - graph: graph as networkX graph
        - coms: community memberships
    Returns: three scores as follows,
        (1) ranking with respect to proportion of grpah nodes that are in the community --> \in [0,1]
        (2) intra_edges/edges_with_at_lest_one_node_in_community --> \in [0,1]
        (3) overall score = ((1) + (2) )/2
    """
    # (1)
    idx = list(coms.keys())
    com_len = [len(coms[i]) for i in idx]
    ranks = stats.rankdata(com_len, "average") / len(com_len)
    coms_score_nodes = {j: round(ranks[i], 1) for i, j in enumerate(idx)}

    # (2)
    coms_score_edges = {k: get_com_density(coms[k], graph) for k in range(len(coms))}

    # (3)
    coms_score_overall = {
        k: (coms_score_nodes[k] + coms_score_edges[k]) / 2 for k in range(len(coms))
    }

    return coms_score_nodes, coms_score_edges, coms_score_overall


def get_communities(graph):
    #     community detection
    #     s = time()
    node_com = best_partition(graph)
    coms = {}
    for k, v in node_com.items():
        coms.setdefault(v, []).append(k)
    #     print('Community detection finished. Elapsed: ',time()-s)
    return coms, node_com


def get_com_density(com, graph):
    """
    Input:
        - graph: networkX graph
        - com: list of nodes
    Return; num_edges_inside_com/num_all_com_node_edges
    """
    subg = graph.subgraph(com)
    intra = subg.number_of_edges()
    all_e = len([e for e in graph.edges() if e[0] in subg or e[1] in subg])
    return intra / all_e


def get_node(graph, num, mode="rand", coms_score=None, coms=None):
    """
    Pick 'num' nodes from 'graph' randomly selected with a biasbased on 'mode'
    The parameters 'coms' and 'coms_score' is only used for mode=coms (bias with respect to community score)
    """
    nodes = graph.nodes()
    if mode == "rand":
        return np.random.choice(nodes, num, replace=False)  # drawn unformaly at random
    elif mode == "deg":
        probs = dict(graph.degree())
        sum_prob = sum(list(probs.values()))
        probs = {k: v / sum_prob for k, v in probs.items()}
        return np.random.choice(nodes, num, replace=False, p=[probs[i] for i in nodes])
    elif mode == "com":  # com != None
        # assing the community score to all its members
        probs = {
            n: coms_score[coms[n]] for n in graph.nodes()
        }  # all scores are already between 0 and 1
        sum_prob = sum(list(probs.values()))
        probs = {k: v / sum_prob for k, v in probs.items()}  # to make probs sum to 1
        return np.random.choice(nodes, num, replace=False, p=[probs[i] for i in nodes])
    else:
        print(f"ERROR: Unknown mode {mode}.")
        return 0


def main():
    path = "../data/merged/"
    save2 = "./data/"
    if not os.path.exists(save2):
        os.mkdir(save2)

    num_targets = 100
    num_sources = 100
    names = [
        "deezer.pkl",
        "facebook_pages.pkl",
        "github_web_ml.pkl",
        "lastfm.pkl",
        "twitch_en.pkl",
    ]

    for _, _, files in os.walk(path):
        files = [i for i in files if i in names]
        for file in files:
            print("processing: ", file)
            with open(os.path.join(path, file), "rb") as f:
                data = pickle.load(f)
            graph = data["graph"]
            s = time()
            coms, node_com = get_communities(graph)
            print("communities found. elapsed: ", time() - s)
            s = time()
            coms_score_edges, coms_score_nodes, coms_score_overall = get_comscore(
                graph, coms
            )
            print("community scoring done. elapsed: ", time() - s)
            res = dict(
                graph=graph,
                targets_random=get_node(graph, num_targets, "rand"),
                targets_degree=get_node(graph, num_targets, "deg"),
                targets_community=get_node(
                    graph,
                    num_targets,
                    "com",
                    coms=node_com,
                    coms_score=coms_score_overall,
                ),
                sources=get_node(graph, num_sources, "rand"),
                node_com=node_com,
                coms_score_edges=coms_score_edges,
                coms_score_nodes=coms_score_nodes,
                coms_score_overall=coms_score_overall,
            )
            with open(os.path.join(save2, file), "wb") as f:
                pickle.dump(res, f)
            print("processing done.\n")


if __name__ == "__main__":
    main()