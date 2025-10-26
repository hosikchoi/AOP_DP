# dp-aop-path-rec

Dynamic Programming–based recommendation of alternative AOP pathways for common MIE–AO pairs.

This repository implements the pipeline described in the draft:
- **Dynamic Programming-based Recommendation of Alternative AOP Pathways for Common MIE–AO Pairs** (DP_AOP) — core DP on WoE-weighted DAG, top-k paths, exposure mapping.  
- Graph/RAG integration and data-build ideas are compatible with our Neo4j stack for Eco-life(초록누리)×ToxCast×CTD×AOP-Wiki.

## Features
- Load a directed acyclic AOP event graph (MIE → KE → AO) from CSVs or Neo4j.
- Integrate multi-source edge **weights of evidence**: AOP-Wiki qualitative confidence, ToxCast assay signals, literature/NLP scores.
- Compute **optimal path** (and **top-k alternatives**) with a single forward DP pass on a DAG.
- **Exposure mapping**: map first stressor/chemical on each path to Eco-life product counts → product usage ratios.
- Optional **semantic augmentation**: plug an LLM/embedding score into edge weights without changing DP.

## Quickstart
```bash
pip install -r requirements.txt
python -m aopdp.cli --config configs/example.yml
```

### Inputs (by default CSVs under `data/`)
- `events.csv`: event_id,type,name
- `edges.csv`: src_event_id,dst_event_id,wwiki,wtoxcast,wlit   # values in [0,1]
- `chem_map.csv`: event_id,casrn,dtxsid (optional for MIE/stressor mapping)
- `products.csv`: casrn,product_id,category   # Eco-life extraction (optional)

### Outputs
- `outputs/best_path_<AO>_<MIE>.csv` — nodes/edges & cumulative scores
- `outputs/topk_paths_<AO>_<MIE>.csv` — k paths flattened with ranks
- `outputs/exposure_summary_<AO>_<MIE>.csv` — product ratios per chemical

See `configs/example.yml` for knobs.

## Method highlights
- **DP on a weighted DAG**: $F(v)=\max_{u\in pred(v)}[F(u)+w(u,v)]$ and backtrack for $\pi^*.$  
- **Top-k** via edge-masking/Yen-style variants to enumerate plausible alternatives under biological ordering.
- **Integrated weight** $w = \alpha w_\text{wiki} + \beta w_\text{toxcast} + \gamma w_\text{lit},$ $\alpha+\beta+\gamma=1.$

## Neo4j (optional)
- The package can read/write subgraphs with `neo4j` driver if you point a `neo4j:` section in config.

## Citation context
Our implementation follows and operationalizes ideas from our manuscripts and related tools:
- DP formalization, top-k enumeration, exposure mapping, and config knobs: DP_AOP draft.  
- Graph build and Eco-life×ToxCast×CTD×AOP-Wiki integration: Korean Information Systems Society report.  
- Literature-driven extraction and RoG/DP combo (optional semantic augmentation): literature-to-AOP draft.  
- Pulmonary-fibrosis data-mining case study underpinning multi-source evidence: Jeong et al. 2023.  
- Labeled Property Graph & LLM-to-Cypher exploration for AOP-Wiki: AOPWiki-Explorer.  
- Literature KER scoring and visualization that can supply `w_lit`: AOP-helpFinder 3.0.

## License
MIT
