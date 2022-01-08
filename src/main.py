import argparse
import os
import pickle
import sys
from attacker import bfs, dfs, randomwalk
from baselines import run_roam, run_greedy, run_betweenness, run_pagerank, run_maxdeg
from coverd import run_CoVerD
from utils import load_adata, load_ddata, load_nothing_data


DEFENDER = {
    "coverd": run_CoVerD,
    "roam": run_roam,
    "greedy": run_greedy,
    "betweenness": run_betweenness,
    "pagerank": run_pagerank,
    "maxdeg": run_maxdeg,
}
ATTACKER = {"bfs": bfs, "dfs": dfs, "rw": randomwalk}
DATA = ["deezer", "facebook_pages", "github_web_ml", "lastfm", "twitch_en"]


def get_args():
    parser = argparse.ArgumentParser()
    # defender parameters
    parser.add_argument(
        "--defend",
        type=str,
        default=["coverd"],
        choices=[
            "coverd",
            "roam",
            "greedy",
            "nothing",
            "betweenness",
            "pagerank",
            "maxdeg",
        ],
        help="Defender type. Default: coverd.",
        nargs="+",
    )

    # attacker parameters
    parser.add_argument(
        "--attack",
        type=str,
        default=["bfs"],
        choices=["bfs", "dfs", "rw"],
        help="Attacker type. Default: bfs.",
        nargs="+",
    )

    # modes of running:
    #  - defending and generating graph
    #  - attacking a defended/existing graph
    parser.add_argument(
        "--mode", type=str, default="attack", choices=["attack", "defense"]
    )

    # Handling data and results
    parser.add_argument(
        "--name",
        type=str,
        default="lastfm",
        choices=DATA,
        help="The name of the dataset to be used by apath or dpath",
    )
    parser.add_argument(
        "--dpath",
        type=str,
        default="./data/raw",
        help="Path to read the data for defender in pkl file from.",
    )
    parser.add_argument(
        "--apath",
        type=str,
        default="./data/defended",
        help="Path to directory to read the data for attacker in pkl file from.",
    )
    parser.add_argument(
        "--dsave2",
        type=str,
        default="./data/defended",
        help="Path to directory to save the defender results.",
    )
    parser.add_argument(
        "--asave2",
        type=str,
        default="./results",
        help="Path to save the attacker results.",
    )

    args = parser.parse_args()
    if not os.path.exists(args.dsave2):
        os.makedirs(args.dsave2)
        for d in DATA:
            os.mkdir(os.path.join(args.dsave2), d)
    if not os.path.exists(args.asave2):
        os.makedirs(args.asave2)
        for d in DATA:
            os.mkdir(os.path.join(args.asave2), d)
    return args


def defense(args, budgets, num):
    """
    input: graph, communit, target, budgets
    output: graph, sources, target, defend_time
    """
    print("defense mode starts for data ", args.name)
    path = os.path.join(args.dpath, args.name + ".pkl")
    save2 = os.path.join(args.dsave2, args.name)
    graph, targets, sources, node_com = load_ddata(path, num)
    print(" data loaded.")
    for typ, tars in targets.items():
        print(f"  processing targets of type {typ}")
        for defender in args.defend:
            print(f"   processing {defender} defender")
            name = f"{defender}_{typ}.pkl"
            if defender != "nothing":
                res = {"sources": sources, "targets": {}}
                c = 0
                for tar in tars:
                    print(f"    target node {c}:")
                    c += 1
                    subg = graph.subgraph(
                        [n for n, v in node_com.items() if v == node_com[tar]]
                    )
                    res["targets"][tar] = DEFENDER[defender](graph, subg, tar, budgets)
                with open(os.path.join(save2, name), "wb") as f:
                    pickle.dump(res, f)
            else:
                res = {"sources": sources, "targets": tars, "graph": graph}
                with open(os.path.join(save2, name), "wb") as f:
                    pickle.dump(res, f)


def attack(args, num):
    """
    input: graph, sources, target
    output: attack_budget_all, success_all
    """
    path = os.path.join(args.apath, args.name)
    save2 = os.path.join(args.asave2, args.name)
    for root, _, files in os.walk(path):
        for file in files:
            print(f"processing {file}")
            if "nothing" not in file:
                tar_budggraph, sources = load_adata(os.path.join(root, file), num)
                for attack in args.attack:
                    print(f" processing {attack} attack")
                    res = {"sources": sources, "targets": {}}
                    name = file.split(".pkl")[0] + "_" + attack + ".pkl"
                    for tar, budggraph in tar_budggraph.items():
                        res["targets"][tar] = {}
                        for b_g in budggraph:
                            budg = b_g[0]
                            graph = b_g[1]
                            res["targets"][tar][budg] = ATTACKER[attack](
                                graph, sources=sources, target=tar
                            )
                    with open(os.path.join(save2, name), "wb") as f:
                        pickle.dump(res, f)
            else:
                tars, graph, sources = load_nothing_data(os.path.join(root, file), num)
                for attack in args.attack:
                    print(f" processing {attack} attack")
                    res = {"sources": sources, "targets": {}}
                    name = file.split(".pkl")[0] + "_" + attack + ".pkl"
                    for tar in tars:
                        res["targets"][tar] = ATTACKER[attack](
                            graph, sources=sources, target=tar
                        )
                    with open(os.path.join(save2, name), "wb") as f:
                        pickle.dump(res, f)


def main(args):
    budgets = [round(0.001 * i, 3) for i in range(1, 52, 5)]
    num = 5  # pick 5 targets and 5 sources only
    if args.mode == "defense":
        defense(args, budgets, num)
    elif args.mode == "attack":
        attack(args, num)
    else:
        sys.exit(f"ERROR: the mode {args.mode} is not valid.")


if __name__ == "__main__":
    args = get_args()
    main(args)
