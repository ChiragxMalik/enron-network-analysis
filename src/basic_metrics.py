import networkx as nx

def compute_basic_metrics(G):
    """Compute fundamental graph properties."""
    metrics = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "density": nx.density(G),
        "is_directed": G.is_directed(),
    }
    
    # Component analysis
    if G.is_directed():
        metrics["weakly_connected_components"] = nx.number_weakly_connected_components(G)
        metrics["strongly_connected_components"] = nx.number_strongly_connected_components(G)
        largest_cc = max(nx.weakly_connected_components(G), key=len)
    else:
        metrics["connected_components"] = nx.number_connected_components(G)
        largest_cc = max(nx.connected_components(G), key=len)
    
    G_lcc = G.subgraph(largest_cc)
    metrics["lcc_nodes"] = len(G_lcc.nodes())
    metrics["lcc_fraction"] = len(G_lcc.nodes()) / G.number_of_nodes()
    
    # Approximate diameter
    print("Computing approximate diameter...")
    try:
        if G.is_directed():
            metrics["diameter_lcc"] = nx.approximation.diameter(G_lcc.to_undirected())
        else:
            metrics["diameter_lcc"] = nx.approximation.diameter(G_lcc)
        print(f"  Approximate diameter: {metrics['diameter_lcc']}")
    except Exception as e:
        print(f"  Could not compute diameter: {e}")
        metrics["diameter_lcc"] = "N/A"

    metrics["avg_path_length"] = None
    
    return metrics
