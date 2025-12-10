import networkx as nx
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np

try:
    import community as community_louvain
except ImportError:
    import community.community_louvain as community_louvain

def detect_communities(G, config):
    """Detect communities using Louvain algorithm with probabilistic sampling."""
    print("Detecting communities...")
    
    if G.is_directed():
        components = nx.weakly_connected_components(G)
        G_work = G.to_undirected()
    else:
        components = nx.connected_components(G)
        G_work = G
    
    largest_cc = max(components, key=len)
    G_lcc = G_work.subgraph(largest_cc).copy()
    
    print(f"  Largest component: {G_lcc.number_of_nodes()} nodes")
    
    print("  Probabilistic sampling")
    G_sampled = _probabilistic_sampling(G_lcc, sampling_rate=0.8)
    print(f"  Sampled: {G_sampled.number_of_nodes()} nodes ({G_sampled.number_of_nodes()/G_lcc.number_of_nodes()*100:.1f}%)")
    
    # Run Louvain on sampled graph
    partition_sampled = community_louvain.best_partition(G_sampled)
    
    # Propagate partition to full graph
    partition = _propagate_partition(G_lcc, G_sampled, partition_sampled)
    modularity = community_louvain.modularity(partition, G_lcc)
    
    # Community statistics
    community_sizes = {}
    for node, comm in partition.items():
        community_sizes[comm] = community_sizes.get(comm, 0) + 1
    
    sizes_list = sorted(community_sizes.values(), reverse=True)
    
    results = {
        "num_communities": len(set(partition.values())),
        "modularity": modularity,
        "community_sizes": sizes_list,
        "largest_community_size": max(sizes_list),
        "smallest_community_size": min(sizes_list),
        "sampling_method": "probabilistic (80%)",
        "sampling_rate": 0.8
    }
    
    # Save results
    os.makedirs("outputs/metrics", exist_ok=True)
    with open("outputs/metrics/communities.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"  Found {results['num_communities']} communities")
    print(f"  Modularity: {modularity:.3f}")
    print(f"  Sampling method: Probabilistic (80%)")
    print(f"  Saved: outputs/metrics/communities.json")
    
    return partition, results

def _probabilistic_sampling(G, sampling_rate=0.8):
    """
    Probabilistic sampling: Include each node with probability proportional to its degree.
    Higher-degree nodes more likely to be sampled (importance sampling).
    """
    G_sample = G.copy()
    nodes_to_remove = []
    
    # Calculate sampling probability based on degree
    degrees = dict(G.degree())
    mean_degree = np.mean(list(degrees.values()))
    
    for node in G.nodes():
        # Probability: base rate + degree bonus
        # This ensures ~sampling_rate of nodes are included
        degree_factor = degrees[node] / mean_degree
        prob = sampling_rate * degree_factor / (1 + degree_factor)
        
        if np.random.random() > prob:
            nodes_to_remove.append(node)
    
    G_sample.remove_nodes_from(nodes_to_remove)
    return G_sample

def _propagate_partition(G_full, G_sampled, partition_sampled):
    """
    Propagate partition from sampled graph to full graph.
    For nodes not in sample, assign to community of nearest neighbor.
    """
    partition_full = {}
    
    # First, copy partition for sampled nodes
    for node, comm in partition_sampled.items():
        partition_full[node] = comm
    
    # For nodes not in sample, find nearest neighbor in sample
    sampled_nodes = set(G_sampled.nodes())
    unsampled_nodes = set(G_full.nodes()) - sampled_nodes
    
    for node in unsampled_nodes:
        # Find neighbors in sampled graph
        neighbors = list(G_full.neighbors(node))
        sampled_neighbors = [n for n in neighbors if n in sampled_nodes]
        
        if sampled_neighbors:
            # Assign to community of most connected sampled neighbor
            best_neighbor = max(sampled_neighbors, 
                              key=lambda n: len([x for x in G_full.neighbors(n) 
                                               if x in sampled_nodes]))
            partition_full[node] = partition_sampled[best_neighbor]
        else:
            # If no sampled neighbors, create new community
            partition_full[node] = max(partition_sampled.values()) + 1
    
    return partition_full

def visualize_communities(G, partition):
    """Visualize communities with sampled nodes."""
    print("Creating community visualization...")
    
    # Sample 500 nodes for visualization
    nodes = list(partition.keys())
    if len(nodes) > 500:
        sampled_nodes = np.random.choice(nodes, 500, replace=False)
    else:
        sampled_nodes = nodes
    
    G_sample = G.subgraph(sampled_nodes)
    
    # Get community colors (max 20 distinct colors)
    communities = set(partition.values())
    num_communities = len(communities)
    colors = plt.cm.tab20(np.linspace(0, 1, min(20, num_communities)))
    
    node_colors = []
    for node in G_sample.nodes():
        comm = partition[node]
        color_idx = comm % 20
        node_colors.append(colors[color_idx])
    
    # Create layout
    pos = nx.spring_layout(G_sample, k=0.5, iterations=50, seed=42)
    
    # Plot
    plt.figure(figsize=(12, 10))
    nx.draw_networkx_nodes(G_sample, pos, node_color=node_colors, 
                          node_size=50, alpha=0.8)
    nx.draw_networkx_edges(G_sample, pos, alpha=0.2, width=0.5)
    
    plt.title(f'Community Structure ({num_communities} communities, 500 sampled nodes)')
    plt.axis('off')
    plt.tight_layout()
    
    os.makedirs("outputs/plots", exist_ok=True)
    plt.savefig("outputs/plots/community_visualization.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print("  Saved: outputs/plots/community_visualization.png")
