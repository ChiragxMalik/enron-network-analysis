import networkx as nx
import numpy as np
import powerlaw
import matplotlib.pyplot as plt
import json
import os
from tqdm import tqdm

def test_scale_free(G):
    """Test if network follows power-law degree distribution."""
    print("Testing scale-free properties...")
    
    degrees = [d for n, d in G.degree()]
    
    print("  Fitting power-law")
    fit = powerlaw.Fit(degrees, discrete=True, verbose=False)
    R_exp, p_exp = fit.distribution_compare('power_law', 'exponential')
    
    results = {
        "power_law_exponent": float(fit.power_law.alpha),
        "p_value": float(p_exp),
        "is_scale_free": bool(p_exp > 0.05 and R_exp > 0)
    }
    
    print("  Creating plot")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Linear scale
    ax1.hist(degrees, bins=50, alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Degree')
    ax1.set_ylabel('Count')
    ax1.set_title('Degree Distribution')
    
    # Log-log scale with power-law fit
    degree_counts = {}
    for d in degrees:
        degree_counts[d] = degree_counts.get(d, 0) + 1
    
    x = sorted(degree_counts.keys())
    y = [degree_counts[k] for k in x]
    
    ax2.scatter(x, y, alpha=0.6, s=20)
    
    # Plot fitted power-law line
    x_fit = np.logspace(np.log10(min(x)), np.log10(max(x)), 100)
    y_fit = (x_fit ** -fit.power_law.alpha) * (max(y) * (max(x) ** fit.power_law.alpha))
    ax2.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'Power-law fit (γ={fit.power_law.alpha:.2f})')
    
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Degree')
    ax2.set_ylabel('Count')
    ax2.set_title('Degree Distribution (Log-Log)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs("outputs/plots", exist_ok=True)
    plt.savefig("outputs/plots/degree_distribution.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Power-law exponent: {results['power_law_exponent']:.2f}")
    print(f"  Scale-free: {results['is_scale_free']}")
    print("  Saved: outputs/plots/degree_distribution.png")
    
    return results

def calculate_small_world(G):
    """Calculate small-world coefficient."""
    print("Calculating small-world coefficient...")
    
    if G.is_directed():
        largest_cc = max(nx.weakly_connected_components(G), key=len)
        G_lcc = G.subgraph(largest_cc).to_undirected()
    else:
        largest_cc = max(nx.connected_components(G), key=len)
        G_lcc = G.subgraph(largest_cc)
    
    n = G_lcc.number_of_nodes()
    m = G_lcc.number_of_edges()
    
    print("  Clustering coefficient")
    C_actual = nx.average_clustering(G_lcc)
    
    print("  Average path length (sampled)")
    if n > 1000:
        sampled_nodes = np.random.choice(list(G_lcc.nodes()), 1000, replace=False)
        path_lengths = []
        for node in tqdm(sampled_nodes, desc="  Sampling"):
            lengths = nx.single_source_shortest_path_length(G_lcc, node)
            path_lengths.extend(lengths.values())
        L_actual = np.mean(path_lengths)
    else:
        L_actual = nx.average_shortest_path_length(G_lcc)
    
    print("  Random graph comparison")
    p = 2 * m / (n * (n - 1))
    C_random = p
    L_random = np.log(n) / np.log(n * p) if n * p > 1 else float('inf')
    
    # Calculate sigma
    if L_random > 0 and C_random > 0:
        sigma = (C_actual / C_random) / (L_actual / L_random)
    else:
        sigma = None
    
    results = {
        "sigma": float(sigma) if sigma else None,
        "clustering_coeff": float(C_actual),
        "avg_path_length": float(L_actual),
        "clustering_random": float(C_random),
        "path_length_random": float(L_random),
        "is_small_world": bool(sigma > 1) if sigma else False
    }
    
    print(f"  Clustering: {C_actual:.4f} (random: {C_random:.6f})")
    print(f"  Path length: {L_actual:.2f} (random: {L_random:.2f})")
    print(f"  Sigma: {sigma:.2f}" if sigma else "  Sigma: N/A")
    print(f"  Small-world: {results['is_small_world']}")
    
    return results

def save_network_properties(scale_free_results, small_world_results):
    """Save all network properties to JSON."""
    results = {
        "power_law": scale_free_results,
        "small_world": small_world_results
    }
    
    os.makedirs("outputs/metrics", exist_ok=True)
    with open("outputs/metrics/network_properties.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("  Saved: outputs/metrics/network_properties.json")
