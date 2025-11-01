from __future__ import annotations
import numpy as np
import pandas as pd

def integrate_weights(edges: pd.DataFrame, alpha: float, beta: float, gamma: float) -> pd.DataFrame:
    if not np.isclose(alpha+beta+gamma, 1.0):
        raise ValueError("alpha+beta+gamma must be 1.0")
    for col in ["wwiki","wtoxcast","wlit"]:
        if col not in edges.columns:
            edges[col] = 0.0
        edges[col] = edges[col].clip(0,1)
    edges = edges.copy()
    edges["w"] = alpha*edges["wwiki"] + beta*edges["wtoxcast"] + gamma*edges["wlit"]
    return edges

def threshold_and_mask(edges: pd.DataFrame, min_edge_w: float) -> pd.DataFrame:
    return edges[edges["w"] >= min_edge_w].reset_index(drop=True)
