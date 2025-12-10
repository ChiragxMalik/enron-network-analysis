"""
Enron Email Network Analysis
Research-grade tool for analyzing corporate communication networks
"""

import argparse
import yaml
import json
import os
import sys
from datetime import datetime

# Import analysis modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_graph, get_largest_component
from basic_metrics import compute_basic_metrics
from centrality import compute_centralities, identify_power_structure
from community_detection import detect_communities, visualize_communities
from robustness import simulate_targeted_attack, simulate_random_failure, create_robustness_plot, save_robustness_results
from network_properties import test_scale_free, calculate_small_world, save_network_properties
from visualization import plot_power_structure, plot_centrality_comparison

def load_config(config_path):
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

def save_json(data, filepath):
    """Save data as JSON."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filepath}")

def main():
    parser = argparse.ArgumentParser(
        description='Enron Email Network Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--data', help='Override data file path')
    parser.add_argument('--output', help='Override output directory')
    parser.add_argument('--skip-viz', action='store_true', help='Skip visualization generation')
    parser.add_argument('--skip-robustness', action='store_true', help='Skip robustness analysis (slow)')
    parser.add_argument('--skip-properties', action='store_true', help='Skip network properties analysis (slow)')
    parser.add_argument('--skip-community', action='store_true', help='Skip community detection (slow)')
    
    args = parser.parse_args()
    
    # Load configuration
    print("="*60)
    print("ENRON EMAIL NETWORK ANALYSIS")
    print("="*60)
    print(f"\nLoading configuration from: {args.config}")
    config = load_config(args.config)
    
    # Override config with command-line arguments
    if args.data:
        config['data']['input_file'] = args.data
    if args.output:
        config['data']['output_dir'] = args.output
    
    # Create output directory structure
    output_dir = config['data']['output_dir']
    metrics_dir = os.path.join(output_dir, 'metrics')
    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    print(f"Data file: {config['data']['input_file']}")
    print(f"Output directory: {output_dir}")
    
    # Load graph
    print("\n" + "="*60)
    print("STEP 1: Loading Graph")
    print("="*60)
    G = load_graph(config['data']['input_file'])
    
    # Basic metrics
    print("\n" + "="*60)
    print("STEP 2: Computing Basic Metrics")
    print("="*60)
    basic_metrics = compute_basic_metrics(G)
    save_json(basic_metrics, os.path.join(metrics_dir, 'basic_stats.json'))
    
    # Centrality analysis
    print("\n" + "="*60)
    print("STEP 3: Centrality Analysis")
    print("="*60)
    centrality_df = compute_centralities(G, config['analysis']['centrality'])
    centrality_df.to_csv(os.path.join(metrics_dir, 'centrality.csv'), index=False)
    print(f"Saved: {os.path.join(metrics_dir, 'centrality.csv')}")
    
    print("\nTop 10 nodes by PageRank:")
    print(centrality_df.nlargest(10, 'pagerank')[['node', 'degree', 'pagerank', 'betweenness']])
    
    # Power structure analysis
    print("\n" + "="*60)
    print("STEP 4: Power Structure Analysis")
    print("="*60)
    power_structure = identify_power_structure(centrality_df, config['analysis']['power_structure'])
    save_json(power_structure, os.path.join(metrics_dir, 'power_structure.json'))
    
    print(f"Hidden influencers: {len(power_structure['hidden_influencers'])}")
    print(f"Information brokers: {len(power_structure['information_brokers'])}")
    print(f"Power hubs: {len(power_structure['power_hubs'])}")
    
    # Community detection
    if not args.skip_community:
        print("\n" + "="*60)
        print("STEP 5: Community Detection")
        print("="*60)
        partition, community_results = detect_communities(G, config['analysis']['community'])
        
        if not args.skip_viz:
            visualize_communities(G, partition)
    else:
        print("\n" + "="*60)
        print("STEP 5: Community Detection - SKIPPED")
        print("="*60)
        community_results = None
        partition = None
    

    
    # Network properties
    if not args.skip_properties:
        print("\n" + "="*60)
        print("STEP 6: Network Properties Analysis")
        print("="*60)
        
        scale_free_results = test_scale_free(G)
        small_world_results = calculate_small_world(G)
        save_network_properties(scale_free_results, small_world_results)
        
        network_properties = {
            'power_law': scale_free_results,
            'small_world': small_world_results
        }
    else:
        print("\n" + "="*60)
        print("STEP 6: Network Properties Analysis - SKIPPED")
        print("="*60)
        network_properties = None
    
    # Robustness analysis
    if not args.skip_robustness:
        print("\n" + "="*60)
        print("STEP 7: Robustness Analysis")
        print("="*60)
        
        targeted_results = simulate_targeted_attack(G, centrality_df)
        random_results = simulate_random_failure(G)
        
        if not args.skip_viz:
            create_robustness_plot(targeted_results, random_results)
        
        save_robustness_results(targeted_results, random_results)
        
        robustness_results = {
            'targeted': targeted_results,
            'random': random_results
        }
    else:
        print("\n" + "="*60)
        print("STEP 7: Robustness Analysis - SKIPPED")
        print("="*60)
        robustness_results = None
    
    # Visualizations
    if not args.skip_viz:
        print("\n" + "="*60)
        print("STEP 8: Generating Additional Visualizations")
        print("="*60)
        
        dpi = config['visualization']['figure_dpi']
        
        print("Creating power structure map...")
        plot_power_structure(centrality_df, plots_dir, dpi)
        
        print("Creating centrality correlation plot...")
        plot_centrality_comparison(centrality_df, plots_dir, dpi)
        
        print(f"\nAll plots saved to: {plots_dir}")
    
    # Print final summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    print(f"\nNetwork Stats:")
    print(f"  Nodes: {basic_metrics['num_nodes']:,}")
    print(f"  Edges: {basic_metrics['num_edges']:,}")
    print(f"  Density: {basic_metrics['density']:.6f}")
    print(f"  Largest component: {basic_metrics['lcc_fraction']*100:.1f}%")
    
    print(f"\nPower Structure:")
    print(f"  Top influencer: Node {centrality_df.nlargest(1, 'pagerank')['node'].values[0]}")
    print(f"  Hidden influencers: {len(power_structure['hidden_influencers'])}")
    print(f"  Information brokers: {len(power_structure['information_brokers'])}")
    
    if community_results:
        print(f"\nCommunities:")
        print(f"  Found: {community_results['num_communities']}")
        print(f"  Modularity: {community_results['modularity']:.3f}")
        print(f"  Largest: {community_results['largest_community_size']} nodes")
    
    if network_properties:
        print(f"\nNetwork Properties:")
        print(f"  Power-law exponent: {network_properties['power_law']['power_law_exponent']:.2f}")
        print(f"  Small-world sigma: {network_properties['small_world']['sigma']:.2f}")
    
    if robustness_results:
        print(f"\nRobustness:")
        targeted_20 = robustness_results['targeted'][20]['largest_component_pct']
        random_20 = robustness_results['random'][20]['largest_component_pct']
        print(f"  20% targeted removal: {targeted_20:.1f}% remains")
        print(f"  20% random removal: {random_20:.1f}% remains")
    
    # Summary
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"\nResults saved to: {output_dir}")
    print(f"\nMetrics:")
    print(f"  - metrics/basic_stats.json")
    print(f"  - metrics/centrality.csv")
    print(f"  - metrics/communities.json")
    print(f"  - metrics/network_properties.json")
    if robustness_results:
        print(f"  - metrics/robustness.json")
    if not args.skip_viz:
        print(f"\nPlots:")
        print(f"  - plots/degree_distribution.png")
        print(f"  - plots/power_structure_map.png")
        print(f"  - plots/centrality_correlation.png")
        print(f"  - plots/community_visualization.png")
        if robustness_results:
            print(f"  - plots/robustness_analysis.png")
    print(f"\nResult:")
    print(f"  - Pipeline run successfully")
    


if __name__ == "__main__":
    main()
