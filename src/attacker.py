import numpy as np


def bfs(graph, **param):
    sources = param["sources"]
    target = param["target"]
    stop_thr = 10 * graph.number_of_nodes()
    # srouce:(flag,[visted nodes]) and flag is true if in the end we reach the target
    result = {}
    num = 0

    for source in sources:  # repeat the bfs 10 times and get average of length
        num += 1
        visited = set([])
        queue = [source]
        counter = 0
        # path = [] # keep the order of nodes reached
        flag = False

        while counter < stop_thr and len(queue) > 0:
            counter += 1
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            # path.append(current)
            if current == target:
                flag = True
                break
            neighbors = set(list(graph[current])).difference(visited)
            queue += list(neighbors)
            if counter > 0 and counter % 5000 == 0:
                print("\t   BFS", counter, len(visited))

        result[source] = (flag, list(visited), graph.number_of_nodes())
        print(f"\t Source {num} is done.")

    return result


def dfs(graph, **param):
    sources = param["sources"]
    target = param["target"]
    stop_thr = 10 * graph.number_of_nodes()
    # stop_thr = graph.number_of_edges()
    result = (
        {}
    )  # srouce:(flag,[visted nodes]) and flag is true if in the end we reach the target
    num = 0

    for source in sources:
        num += 1
        counter = 0
        queried = set([])
        queue = [source]
        # path = []
        flag = False

        while counter < stop_thr and len(queue) > 0:
            counter += 1
            current = queue.pop(0)
            if current in queried:
                continue
            queried.add(current)
            # path.append(current)
            if current == target:
                flag = True
                break
            neighbors = list(set(list(graph[current])).difference(queried))
            np.random.shuffle(neighbors)
            queue = neighbors + queue

            if counter > 0 and counter % 5000 == 0:
                print("\t   DFS", counter, len(queried))

        result[source] = (flag, list(queried), graph.number_of_nodes())
        print(f"\t Source {num} is done.")

    return result


def randomwalk(graph, **param):
    """
    policy:
        - keep track of nodes and their neighbors in each iteration
        - at each node, jump uniformly at random to an unvisited node, if such a node doesn't exist:
        - jump uniformly at random to an unvisited node from the nodes we have been keeping track of
        - else jump uniformly at random to an unvisited node from overall graph
    """
    sources = param["sources"]
    target = param["target"]
    stop_thr = 10 * graph.number_of_nodes()
    # stop_thr = graph.number_of_edges()
    result = (
        {}
    )  # srouce:(flag,[visted nodes]) and flag is true if in the end we reach the target
    num = 0

    for source in sources:  # repeat the bfs 10 times and get average of length
        num += 1
        visited = set([])
        current = source
        nodes = {source}
        counter = 0
        # path = [] # keep the order of nodes reached
        flag = False

        while counter < stop_thr:
            counter += 1
            nodes.update(graph[current])
            if current in visited:
                continue
            visited.add(current)
            # path.append(current)
            if current == target:
                flag = True
                break

            neighbors = set(list(graph[current])).difference(visited)
            tmp = [n for n in nodes if n not in visited]
            if len(neighbors) > 0:
                current = np.random.choice(list(neighbors))
            elif len(tmp) > 0:
                current = np.random.choice(tmp)
            else:
                current = np.random.choice([n for n in graph if n not in visited])

            if counter % 5000 == 0:
                print("\t   RW", counter, len(visited))

        result[source] = (flag, list(visited), graph.number_of_nodes())
        print(f"\t Source {num} is done.")

    return result
