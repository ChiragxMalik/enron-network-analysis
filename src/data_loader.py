import networkx as nx
import os

def load_graph(file_path, directed=False):
    """Load graph from edge list file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    graph_type = nx.DiGraph() if directed else nx.Graph()
    
    G = nx.read_edgelist(
        file_path,
        comments='#',
        create_using=graph_type,
        nodetype=int
    )
    
    print(f"Loaded graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G

def get_largest_component(G):
    """Extract largest connected component."""
    if G.is_directed():
        components = nx.weakly_connected_components(G)
    else:
        components = nx.connected_components(G)
    
    largest_cc = max(components, key=len)
    G_lcc = G.subgraph(largest_cc).copy()
    
    print(f"Largest component: {G_lcc.number_of_nodes()} nodes ({G_lcc.number_of_nodes()/G.number_of_nodes()*100:.1f}%)")
    return G_lcc
