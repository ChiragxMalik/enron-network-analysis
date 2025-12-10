# Enron Email Network Analysis

Analysis of corporate communication networks during organizational crisis using complex network techniques.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```
## NOTE

- Full Run time can take around 10 to 15 minutes (depending on system configuration)

## What This Does

Analyzes the Enron email network (36,692 nodes, 183,831 edges) to understand:
- **Power Structure**: Key influencers and information brokers
- **Organization**: Community structure and departmental boundaries  
- **Vulnerability**: Network resilience to targeted attacks
- **Properties**: Scale-free and small-world characteristics

## Techniques & Algorithms Used

| Component | Technique | Purpose |
|-----------|-----------|---------|
| **Centrality** | Degree, PageRank, Betweenness | Identify influential nodes |
| **Community Detection** | Louvain Algorithm + Probabilistic Sampling | Find organizational clusters |
| **Sampling** | Importance Sampling (80% rate) | Efficient community detection |
| **Scale-Free Test** | Power-Law Fitting (powerlaw library) | Validate degree distribution |
| **Small-World** | Clustering Coefficient & Path Length | Measure network efficiency |
| **Robustness** | Targeted vs Random Attack Simulation | Test network vulnerability |

## Key Findings

- **36,692 nodes**, 183,831 edges (sparse network)
- **207 communities** with modularity 0.605
- **Small-world sigma: 1,743** (highly efficient)
- **5% targeted removal → 34.6% remains** (extremely vulnerable)
- **20% random removal → 67.1% remains** (resilient to random failures)

## Project Structure

```
├── main.py                 # Main analysis pipeline
├── config.yaml             # Configuration parameters
├── requirements.txt        # Python dependencies
├── data/
│   └── Email-Enron.txt    # SNAP edge list
├── src/
│   ├── data_loader.py
│   ├── basic_metrics.py
│   ├── centrality.py
│   ├── community_detection.py
│   ├── network_properties.py
│   ├── robustness.py
│   └── visualization.py
└── outputs/
    ├── metrics/            # JSON/CSV results
    └── plots/              # Visualizations
```

## Usage

```bash
# Full analysis
python main.py

# Skip slow parts
python main.py --skip-robustness --skip-properties

# Custom config
python main.py --config custom.yaml
```

## Outputs

**Metrics** (outputs/metrics/):
- `basic_stats.json` - Network statistics
- `centrality.csv` - Node rankings
- `communities.json` - Community structure
- `network_properties.json` - Scale-free & small-world
- `robustness.json` - Attack simulation results

**Plots** (outputs/plots/):
- Degree distribution with power-law fit
- Power structure map (PageRank vs Degree)
- Centrality correlations
- Community visualization
- Robustness analysis (targeted vs random)

## Performance

- Runtime: 5-10 minutes (full analysis)
- Handles 36,692 nodes efficiently
- Probabilistic sampling for fast community detection
- Progress bars for all operations

## Dataset

SNAP Enron Email Network
- Source: https://snap.stanford.edu/data/email-Enron.html
- Time period: 1999-2002
- Type: Undirected, unweighted communication graph
