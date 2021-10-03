import networkx as nx
from time import time
from utils import *
from baselines import roam


def run_CoVerD(graph,subg,target,budgets):
    '''
    input: original graph, community of the target node as a subgraph, target node
    '''
    result = {}
    for idx in budgets:
        s = time()
        result[idx] = CoVerD(graph,subg,target,idx)
        print(f'\t budget {idx} done! Elapsed: {time()-s}')
    return result


def CoVerD(graph,subg,target,idx):
    s = time()
    budget = idx*graph.number_of_edges()
    community = subg.copy()
    G = graph.copy()
    actions = {'rem':0,'add':0}
    stop = False
    while sum(actions.values()) <= budget and not stop:
        # remove target's neighbors that are outdie the community
        out_neigh = sorted([(node,G.degree(node)) for node in G[target] if
                            node not in community],key=lambda x:x[1],reverse=True)
        for node in out_neigh:
            node = node[0]
            G.remove_edge(target,node)
            if not nx.is_connected(G):
                G.add_edge(target,node)
                continue
            actions['rem'] += 1
            if sum(actions.values()) > budget:
                break
        if sum(actions.values()) > budget:
            break   
            
        # print('1st milestone done.')


        # roam
        orig_neigh = list(G[target])
        while G.degree(target) > 1:
            G,spent = roam(G,target,budget=1)
            removed = [(target,n) for n in community[target] if n not in G[target]]
            added = [e for e in G.edges() if
                        e[0] in community and e[1] in community and e not in community.edges()]

            community.add_edges_from(added)
            community.remove_edges_from(removed)
            actions['rem'] += 1
            actions['add'] += (spent-1)
            if sum(actions.values()) >= budget:
                    break
        if sum(actions.values()) >= budget:
                    break
        # print('2nd milestone done.')



        # 1hop + 2nd hop -- no unnecessar addition -- taking care of G not being disconnected
        for neigh in orig_neigh:
            # 1st hop
            for neigh2 in [i for i in G[neigh] if i not in community]:
                G.remove_edge(neigh,neigh2)
                if not nx.is_connected(G):
                    G.add_edge(neigh,neigh2)
                    continue
                actions['rem'] += 1
                if sum(actions.values()) >= budget:
                    break
            if sum(actions.values()) >= budget:
                    break
            nscores = {node:community.degree(node)/G.degree(node) for node in community.nodes()}
            # 2nd hop
            for neigh2 in [i for i in G[neigh] if i in community and i!= target]:
                if nscores[neigh2] < 1:
                    G.remove_edge(neigh,neigh2)
                    if not nx.is_connected(G):
                        G.add_edge(neigh,neigh2)
                        continue
                    community.remove_edge(neigh,neigh2)
                    actions['rem'] += 1
                if sum(actions.values()) >= budget:
                    break
            if sum(actions.values()) >= budget:
                    break
        if sum(actions.values()) >= budget:
                    break

        # print('3rd milestone done.')

        # build loyalty chamber
        # remove edges between nodes with highest score difference inside the community wihtout disconnecting G
        nscores = {node:community.degree(node)/G.degree(node) for node in community.nodes()
                    if node!= target}
        cand = sorted([((n1,n2),s1-s2) for n1,s1 in nscores.items()
                for n2,s2 in nscores.items() if s1==1 and s2<1 and n1!=n2 
                and (n1,n2) in community.edges()],key=lambda x:x[1],reverse=True)
        cand = [i[0] for i in cand]
        for edge in cand:
            G.remove_edges_from([edge])
            if not nx.is_connected(G):
                G.add_edges_from([edge])
                continue
            community.remove_edges_from([edge])
            actions['rem'] += 1
            if sum(actions.values()) >= budget:
                    break
        # print('4th milestone done.')
        

        stop = True
    e = time()-s
    return {'graph':G.copy(),'community':community.copy(),'num_del_edges':actions['rem'],
                      'num_add_edges':actions['add'],'dtime':e}