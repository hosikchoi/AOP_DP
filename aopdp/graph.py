from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable, Optional
import pandas as pd
import networkx as nx

EVENT_TYPES = {"MIE","KE","AO"}

@dataclass
class Event:
    event_id: str
    etype: str
    name: str = ""

@dataclass
class Edge:
    src: str
    dst: str
    wwiki: float = 0.0
    wtoxcast: float = 0.0
    wlit: float = 0.0

class AOPGraph:
    def __init__(self):
        self.g = nx.DiGraph()

    @classmethod
    def from_csv(cls, data_dir: str) -> "AOPGraph":
        ev = pd.read_csv(f"{data_dir}/events.csv")
        ed = pd.read_csv(f"{data_dir}/edges.csv")
        g = cls()
        for _, r in ev.iterrows():
            etype = str(r['type']).upper()
            if etype not in EVENT_TYPES:
                raise ValueError(f"Invalid event type {etype} for {r['event_id']}")
            g.g.add_node(r['event_id'], type=etype, name=r.get('name',''))
        for _, r in ed.iterrows():
            g.g.add_edge(r['src_event_id'], r['dst_event_id'],
                         wwiki=float(r.get('wwiki',0)),
                         wtoxcast=float(r.get('wtoxcast',0)),
                         wlit=float(r.get('wlit',0)))
        if not nx.is_directed_acyclic_graph(g.g):
            # Allow cycles in raw; break them conservatively
            g.g = nx.DiGraph(nx.algorithms.dag.transitive_reduction(nx.DiGraph(g.g)))
        return g

    def subgraph_mie_to_ao(self, mie: str, ao: str, max_hops: int = 6) -> "AOPGraph":
        # BFS to collect nodes within hop constraint
        visited = set([mie])
        frontier = [mie]
        hops = 0
        while frontier and hops < max_hops:
            nxt = []
            for u in frontier:
                for v in self.g.successors(u):
                    if v not in visited:
                        visited.add(v)
                        nxt.append(v)
            frontier = nxt
            hops += 1
        # ensure AO exists even if not reached
        if ao not in visited and ao in self.g:
            visited.add(ao)
        sg = self.g.subgraph(visited).copy()
        h = AOPGraph()
        h.g = sg
        return h

    def edges_df(self) -> pd.DataFrame:
        rows = []
        for u, v, d in self.g.edges(data=True):
            rows.append({
                "src": u, "dst": v, **{k:d.get(k,0.0) for k in ["wwiki","wtoxcast","wlit"]}
            })
        return pd.DataFrame(rows)

    def nodes_df(self) -> pd.DataFrame:
        rows = []
        for n, d in self.g.nodes(data=True):
            rows.append({"event_id": n, "type": d.get("type",""), "name": d.get("name","")})
        return pd.DataFrame(rows)
