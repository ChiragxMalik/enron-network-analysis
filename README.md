# Enron Email Network Analysis

Complex Networks Project - Fall 2025

## Project Structure

```
enron-project/
│
├── data/
│   └── Email-Enron.txt        # SNAP edge list
├── src/
│   └── analysis.py            # Main analysis script
├── outputs/
│   ├── metrics.json           # Basic graph statistics
│   ├── centrality.csv         # Node centrality measures
│   └── plots/                 # Visualizations
└── README.md
```

## Setup

Install required libraries:

```bash
pip install networkx matplotlib pandas
```

## Running the Analysis

```bash
cd src
python analysis.py
```

## Outputs

The script generates:

- `outputs/metrics.json` - Basic graph properties (nodes, edges, density, components, diameter)
- `outputs/centrality.csv` - Node centrality metrics (degree, PageRank, betweenness)
- `outputs/plots/degree_dist.png` - Degree distribution plot (log-log scale)

## Key Metrics Computed

1. **Basic Statistics**: Node count, edge count, density, connected components
2. **Centrality Measures**: 
   - Degree centrality
   - PageRank (α=0.85)
   - Betweenness centrality (approximate, k=1000 samples)
3. **Degree Distribution**: Log-log histogram to identify scale-free properties

## Next Steps

- Community detection (Louvain algorithm)
- Temporal analysis
- Robustness testing (node removal)
- Weighted graph analysis
