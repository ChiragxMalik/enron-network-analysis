# src/analysis.py
import networkx as nx
import pandas as pd
import json
import matplotlib.pyplot as plt
import os

DATA_PATH = "../data/Email-Enron.txt"

def load_graph():
    G = nx.read_edgelist(
        DATA_PATH,
        create_using=nx.DiGraph(),     # Enron is directed
        nodetype=int
    )
    print(f"Nodes: {G.number_of_nodes()}  Edges: {G.number_of_edges()}")
    return G

def compute_basic_stats(G):
    stats = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "density": nx.density(G),
        "is_directed": G.is_directed(),
        "weakly_connected_components": nx.number_weakly_connected_components(G),
    }

    # Diameter only if graph is connected; otherwise use largest component
    largest_cc = max(nx.weakly_connected_components(G), key=len)
    G_lcc = G.subgraph(largest_cc)
    try:
        stats["diameter_lcc"] = nx.diameter(G_lcc.to_undirected())
    except:
        stats["diameter_lcc"] = None

    os.makedirs("../outputs", exist_ok=True)
    with open("../outputs/metrics.json", "w") as f:
        json.dump(stats, f, indent=4)

    print(stats)

def compute_centralities(G, k_sample=1000):
    print("Computing centrality...")

    degree = dict(G.degree())
    pagerank = nx.pagerank(G, alpha=0.85)
    betweenness = nx.betweenness_centrality(G, k=k_sample)  # sampling approx

    df = pd.DataFrame({
        "node": list(G.nodes()),
        "degree": [degree[n] for n in G.nodes()],
        "pagerank": [pagerank[n] for n in G.nodes()],
        "betweenness": [betweenness[n] for n in G.nodes()],
    })

    df.to_csv("../outputs/centrality.csv", index=False)
    print("Centralities saved → outputs/centrality.csv")
    
    # Print top 10 by PageRank
    print("\nTop 10 nodes by PageRank:")
    print(df.nlargest(10, "pagerank"))

def plot_degree_distribution(G):
    degrees = [deg for _, deg in G.degree()]
    
    os.makedirs("../outputs/plots", exist_ok=True)
    plt.figure()
    plt.hist(degrees, bins=50)
    plt.yscale("log")
    plt.xscale("log")
    plt.title("Degree Distribution (log-log)")
    plt.xlabel("Degree")
    plt.ylabel("Count")
    plt.savefig("../outputs/plots/degree_dist.png")
    print("Saved → outputs/plots/degree_dist.png")

if __name__ == "__main__":
    G = load_graph()
    compute_basic_stats(G)
    compute_centralities(G)
    plot_degree_distribution(G)
