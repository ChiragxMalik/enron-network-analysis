import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")

def plot_power_structure(centrality_df, output_dir, dpi=150):
    """Scatter plot: PageRank vs Degree, colored by betweenness."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    scatter = ax.scatter(
        centrality_df['degree'],
        centrality_df['pagerank'],
        c=centrality_df['betweenness'],
        s=50,
        alpha=0.6,
        cmap='viridis'
    )
    
    ax.set_xlabel('Degree')
    ax.set_ylabel('PageRank')
    ax.set_title('Power Structure Map\n(Color = Betweenness Centrality)')
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Betweenness')
    
    # Highlight top nodes
    top_pr = centrality_df.nlargest(10, 'pagerank')
    ax.scatter(top_pr['degree'], top_pr['pagerank'], 
               s=200, facecolors='none', edgecolors='red', linewidths=2, label='Top 10 PageRank')
    
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'power_structure_map.png'), dpi=dpi, bbox_inches='tight')
    plt.close()

def plot_centrality_comparison(centrality_df, output_dir, dpi=150):
    """Compare different centrality measures."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Degree vs PageRank
    axes[0, 0].scatter(centrality_df['degree'], centrality_df['pagerank'], alpha=0.5)
    axes[0, 0].set_xlabel('Degree')
    axes[0, 0].set_ylabel('PageRank')
    axes[0, 0].set_title('Degree vs PageRank')
    
    # Degree vs Betweenness
    axes[0, 1].scatter(centrality_df['degree'], centrality_df['betweenness'], alpha=0.5)
    axes[0, 1].set_xlabel('Degree')
    axes[0, 1].set_ylabel('Betweenness')
    axes[0, 1].set_title('Degree vs Betweenness')
    
    # PageRank vs Betweenness
    axes[1, 0].scatter(centrality_df['pagerank'], centrality_df['betweenness'], alpha=0.5)
    axes[1, 0].set_xlabel('PageRank')
    axes[1, 0].set_ylabel('Betweenness')
    axes[1, 0].set_title('PageRank vs Betweenness')
    
    # Centrality distributions
    axes[1, 1].hist(centrality_df['degree_norm'], bins=30, alpha=0.5, label='Degree')
    axes[1, 1].hist(centrality_df['pagerank_norm'], bins=30, alpha=0.5, label='PageRank')
    axes[1, 1].hist(centrality_df['betweenness_norm'], bins=30, alpha=0.5, label='Betweenness')
    axes[1, 1].set_xlabel('Normalized Centrality')
    axes[1, 1].set_ylabel('Count')
    axes[1, 1].set_title('Centrality Distributions')
    axes[1, 1].legend()
    axes[1, 1].set_yscale('log')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'centrality_correlation.png'), dpi=dpi, bbox_inches='tight')
    plt.close()
