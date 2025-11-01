import argparse, yaml, os, pandas as pd, networkx as nx
from .graph import AOPGraph
from .weights import integrate_weights, threshold_and_mask
from .dp import topk_paths_by_masking
from .exposure import product_ratio, map_first_node_chemicals

def run(config_path: str):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    mie = cfg["run"]["mie"]
    ao  = cfg["run"]["ao"]
    k   = int(cfg["run"]["top_k"])
    alpha, beta, gamma = float(cfg["run"]["alpha"]), float(cfg["run"]["beta"]), float(cfg["run"]["gamma"])
    min_edge_w = float(cfg["run"]["min_edge_w"])
    max_hops = int(cfg["run"].get("max_hops", 6))
    loader = cfg["input"]["loader"]
    data_dir = cfg["input"]["data_dir"]
    out_dir = cfg["output"]["dir"]
    os.makedirs(out_dir, exist_ok=True)

    # Load graph
    if loader == "csv":
        g = AOPGraph.from_csv(data_dir)
    else:
        # Placeholder: Neo4j loader could be added here
        g = AOPGraph.from_csv(data_dir)
    sg = g.subgraph_mie_to_ao(mie, ao, max_hops=max_hops)

    # Integrate weights
    ed = sg.edges_df()
    ed = integrate_weights(ed, alpha, beta, gamma)
    ed = threshold_and_mask(ed, min_edge_w)

    # Build weighted subgraph
    WG = sg.g.copy()
    for _, r in ed.iterrows():
        if WG.has_edge(r["src"], r["dst"]):
            WG.edges[r["src"], r["dst"]]["w"] = float(r["w"])

    # Compute top-k
    results = topk_paths_by_masking(WG, mie, ao, k=k, weight_key="w")
    flat = []
    for rank, (path, score) in enumerate(results, start=1):
        for i in range(len(path)-1):
            u,v = path[i], path[i+1]
            w = WG.edges[u,v].get("w",0.0)
            flat.append({"rank": rank, "u": u, "v": v, "w": w, "cum_score": score})
    paths_only = [p for p,_ in results]

    pd.DataFrame(flat).to_csv(f"{out_dir}/topk_paths_{ao}_{mie}.csv", index=False)

    # Exposure mapping (optional)
    chem_map_fp = os.path.join(data_dir,"chem_map.csv")
    prod_fp = os.path.join(data_dir,"products.csv")
    if os.path.exists(chem_map_fp) and os.path.exists(prod_fp):
        chem_map = pd.read_csv(chem_map_fp)
        prods = pd.read_csv(prod_fp)
        first_chem = map_first_node_chemicals(paths_only, chem_map)
        ratios = product_ratio(prods)
        exp = first_chem.merge(ratios, on="casrn", how="left").sort_values(["rank","product_ratio"], ascending=[True,False])
        exp.to_csv(f"{out_dir}/exposure_summary_{ao}_{mie}.csv", index=False)

    # Best path dump
    if results:
        best_path, best_score = results[0]
        with open(f"{out_dir}/best_path_{ao}_{mie}.csv","w",encoding="utf-8") as f:
            f.write("node
")
            for n in best_path: f.write(f"{n}\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config","-c", required=True, help="Path to YAML config")
    args = ap.parse_args()
    run(args.config)

if __name__ == "__main__":
    main()
