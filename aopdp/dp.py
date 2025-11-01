from __future__ import annotations
from typing import Dict, List, Tuple
import networkx as nx
import pandas as pd
import numpy as np

def dp_longest_path_dag(G: nx.DiGraph, source: str, target: str, weight_key: str = "w"):
    topo = list(nx.topological_sort(G))
    F = {n: -np.inf for n in G.nodes}
    prev = {n: None for n in G.nodes}
    if source not in G or target not in G:
        return [], -np.inf
    F[source] = 0.0
    for v in topo:
        for u in G.predecessors(v):
            w = G.edges[u, v].get(weight_key, 0.0)
            if F[u] + w > F[v]:
                F[v] = F[u] + w
                prev[v] = u
    # backtrack
    if not np.isfinite(F[target]):
        return [], -np.inf
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path = path[::-1]
    return path, float(F[target])

def topk_paths_by_masking(G: nx.DiGraph, source: str, target: str, k: int = 5, weight_key: str = "w"):
    # Simple k-best via iterative masking of one edge from previous best
    results = []
    used_masks = set()
    base_G = G.copy()
    for _ in range(k):
        path, score = dp_longest_path_dag(G, source, target, weight_key)
        if not path or not np.isfinite(score):
            break
        results.append((path, score))
        # generate next candidates by masking each edge in current best
        best_edges = list(zip(path[:-1], path[1:]))
        masked_once = False
        for e in best_edges:
            if e in used_masks:
                continue
            used_masks.add(e)
            G = base_G.copy()
            if G.has_edge(*e):
                G.remove_edge(*e)
                masked_once = True
                break
        if not masked_once:
            break
    return results
