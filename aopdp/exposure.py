import pandas as pd

def product_ratio(products_df: pd.DataFrame) -> pd.DataFrame:
    # products_df: casrn, product_id, category
    counts = products_df.groupby("casrn")["product_id"].nunique().rename("product_count").reset_index()
    total = counts["product_count"].sum()
    counts["product_ratio"] = counts["product_count"] / total if total > 0 else 0.0
    return counts.sort_values("product_ratio", ascending=False)

def map_first_node_chemicals(paths: list[list[str]], chem_map_df: pd.DataFrame) -> pd.DataFrame:
    # chem_map_df: event_id, casrn, dtxsid
    out = []
    chem_map = chem_map_df.dropna().drop_duplicates(subset=["event_id","casrn"])
    for rank, p in enumerate(paths, start=1):
        if not p: 
            continue
        first = p[0]
        m = chem_map[chem_map["event_id"] == first]
        if len(m):
            for _, r in m.iterrows():
                out.append({"rank": rank, "event_id": first, "casrn": r["casrn"], "dtxsid": r.get("dtxsid","")})
    return pd.DataFrame(out)
