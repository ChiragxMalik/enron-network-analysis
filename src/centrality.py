import networkx as nx
import pandas as pd
from tqdm import tqdm

def compute_centralities(G, config):
    """Compute centrality measures: degree, PageRank, betweenness."""
    print("Computing centrality metrics...")
    
    centrality_data = {"node": list(G.nodes())}
    
    print("  Degree centrality")
    degree = dict(G.degree())
    centrality_data["degree"] = [degree[n] for n in G.nodes()]
    
    print("  PageRank")
    alpha = config.get('pagerank_alpha', 0.85)
    pagerank = nx.pagerank(G, alpha=alpha)
    centrality_data["pagerank"] = [pagerank[n] for n in G.nodes()]
    
    print("  Betweenness centrality (sampled)")
    k_samples = config.get('betweenness_k_samples', 1000)
    betweenness = nx.betweenness_centrality(G, k=min(k_samples, G.number_of_nodes()))
    centrality_data["betweenness"] = [betweenness[n] for n in G.nodes()]
    
    df = pd.DataFrame(centrality_data)
    
    # Normalize
    df['degree_norm'] = df['degree'] / df['degree'].max()
    df['pagerank_norm'] = df['pagerank'] / df['pagerank'].max()
    df['betweenness_norm'] = df['betweenness'] / df['betweenness'].max()
    
    return df

def identify_power_structure(df, config):
    """Identify hidden influencers, brokers, and power hubs."""
    
    # Hidden influencers: high PageRank but lower degree rank
    df['pagerank_rank'] = df['pagerank'].rank(ascending=False)
    df['degree_rank'] = df['degree'].rank(ascending=False)
    df['rank_difference'] = df['degree_rank'] - df['pagerank_rank']
    
    top_pr = df.nlargest(100, 'pagerank')
    hidden_influencers = top_pr[top_pr['rank_difference'] > 50].sort_values('pagerank', ascending=False)
    
    # Information brokers: high betweenness/degree ratio
    df['brokerage_score'] = df['betweenness'] / (df['degree'] + 1)
    bet_threshold = df['betweenness'].quantile(config.get('betweenness_threshold', 0.9))
    
    brokers = df[df['betweenness'] >= bet_threshold].sort_values('brokerage_score', ascending=False)
    
    # Power hubs: high on all metrics
    power_hubs = df[
        (df['degree_norm'] >= 0.8) & 
        (df['pagerank_norm'] >= 0.8) & 
        (df['betweenness_norm'] >= 0.8)
    ].sort_values('pagerank', ascending=False)
    
    return {
        "hidden_influencers": hidden_influencers.head(20).to_dict('records'),
        "information_brokers": brokers.head(20).to_dict('records'),
        "power_hubs": power_hubs.to_dict('records')
    }
