import numpy as np
import pickle


def load_ddata(path, num):
    """
    Load data for defender.
    Input: 
        - path: path to pickled file
        - num: number of (source,target) pairs
    Return: graph, target nodes, community assignment, source nodes
    """
    with open(path, "rb") as f:
        data = pickle.load(f)
    graph = data["graph"]
    targets = {
        "random": data["targets_random"][:num],
        "degree": data["targets_degree"][:num],
        "community": data["targets_community"][:num],
    }
    sources = data["sources"][:num]
    node_com = data["node_com"]
    return graph, targets, sources, node_com


def load_adata(path, num):
    """
    Load data for attacker.
    Input: 
        - path: path to pickled file
        - num: number of (source,target) pairs
    Return: graph, sources, targets
    """
    with open(path, "rb") as f:
        data = pickle.load(f)
    sources = data["sources"][:num]
    targets = list(data["targets"])[:num]
    tar_budggraph = {
        k: [(kk, vv["graph"]) for kk, vv in v.items()]
        for k, v in data["targets"].items()
        if k in targets
    }
    return tar_budggraph, sources


def load_nothing_data(path, num):
    """
    Load data for "do-nothing" scenario.
    Input: 
        - path: path to pickled file
        - num: number of (source,target) pairs
    Result: graph, sources, targets
    """
    with open(path, "rb") as f:
        data = pickle.load(f)
    sources = data["sources"][:num]
    targets = data["targets"][:num]
    graph = data["graph"]
    return targets, graph, sources


def random_node(node, community, graph):
    # the node is outside target's community and only connected to target
    # pick a random node in G that is not in community to connect this to
    cands = [i for i in graph if i not in community and i != node]
    return np.random.choice(cands)


def random_edge(node, community, graph):
    # the node is outside target's community and only connected to target
    # pick a random node in G that is not in community to connect this to
    cands = [i for i in graph if i not in community and i != node]
    return (node, np.random.choice(cands))
