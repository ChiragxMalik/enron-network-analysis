import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from tqdm import tqdm
import pandas as pd

def simulate_targeted_attack(G, centrality_df):
    """Simulate targeted attack by removing high PageRank nodes."""
    print("Simulating targeted attack...")
    
    percentages = [1, 5, 10, 20]
    results = {}
    original_size = G.number_of_nodes()
    
    sorted_nodes = centrality_df.nlargest(int(original_size * 0.2), 'pagerank')['node'].tolist()
    
    for pct in tqdm(percentages, desc="  Targeted"):
        G_copy = G.copy()
        num_to_remove = int(original_size * pct / 100)
        nodes_to_remove = sorted_nodes[:num_to_remove]
        
        G_copy.remove_nodes_from(nodes_to_remove)
        
        # Measure largest component
        if G_copy.is_directed():
            components = list(nx.weakly_connected_components(G_copy))
        else:
            components = list(nx.connected_components(G_copy))
        
        if components:
            largest_cc_size = len(max(components, key=len))
        else:
            largest_cc_size = 0
        
        results[pct] = {
            "largest_component_size": largest_cc_size,
            "largest_component_pct": (largest_cc_size / original_size) * 100,
            "num_components": len(components)
        }
    
    print(f"  Targeted attack complete")
    return results

def simulate_random_failure(G):
    """Simulate random node failure with multiple trials."""
    print("Simulating random failure...")
    
    percentages = [1, 5, 10, 20]
    num_trials = 5
    results = {}
    original_size = G.number_of_nodes()
    
    for pct in tqdm(percentages, desc="  Random"):
        trial_results = []
        
        for trial in range(num_trials):
            G_copy = G.copy()
            num_to_remove = int(original_size * pct / 100)
            nodes_to_remove = np.random.choice(list(G.nodes()), num_to_remove, replace=False)
            
            G_copy.remove_nodes_from(nodes_to_remove)
            
            # Measure largest component
            if G_copy.is_directed():
                components = list(nx.weakly_connected_components(G_copy))
            else:
                components = list(nx.connected_components(G_copy))
            
            if components:
                largest_cc_size = len(max(components, key=len))
            else:
                largest_cc_size = 0
            
            trial_results.append({
                "largest_component_size": largest_cc_size,
                "largest_component_pct": (largest_cc_size / original_size) * 100
            })
        
        # Calculate mean and std
        mean_size = np.mean([r['largest_component_size'] for r in trial_results])
        mean_pct = np.mean([r['largest_component_pct'] for r in trial_results])
        std_pct = np.std([r['largest_component_pct'] for r in trial_results])
        
        results[pct] = {
            "largest_component_size": mean_size,
            "largest_component_pct": mean_pct,
            "std": std_pct
        }
    
    print(f"  Random failure complete")
    return results

def create_robustness_plot(targeted_results, random_results):
    """Create robustness comparison plot."""
    print("Creating robustness plot...")
    
    percentages = sorted(targeted_results.keys())
    
    targeted_pcts = [targeted_results[p]['largest_component_pct'] for p in percentages]
    random_pcts = [random_results[p]['largest_component_pct'] for p in percentages]
    random_stds = [random_results[p]['std'] for p in percentages]
    
    plt.figure(figsize=(10, 6))
    
    plt.plot(percentages, targeted_pcts, 'r-o', linewidth=2, markersize=8, label='Targeted Attack')
    plt.errorbar(percentages, random_pcts, yerr=random_stds, fmt='b-s', linewidth=2, 
                markersize=8, capsize=5, label='Random Failure')
    
    plt.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% Threshold')
    
    plt.xlabel('Percentage of Nodes Removed (%)', fontsize=12)
    plt.ylabel('Largest Component Size (% of original)', fontsize=12)
    plt.title('Network Robustness: Targeted vs Random', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    os.makedirs("outputs/plots", exist_ok=True)
    plt.savefig("outputs/plots/robustness_analysis.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print("  Saved: outputs/plots/robustness_analysis.png")

def save_robustness_results(targeted_results, random_results):
    """Save robustness results to JSON."""
    
    # Find critical points
    critical_targeted = None
    critical_random = None
    
    for pct in sorted(targeted_results.keys()):
        if targeted_results[pct]['largest_component_pct'] < 50 and critical_targeted is None:
            critical_targeted = pct
        if random_results[pct]['largest_component_pct'] < 50 and critical_random is None:
            critical_random = pct
    
    results = {
        "targeted_attack": targeted_results,
        "random_failure": random_results,
        "critical_point_targeted": critical_targeted,
        "critical_point_random": critical_random
    }
    
    os.makedirs("outputs/metrics", exist_ok=True)
    with open("outputs/metrics/robustness.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("  Saved: outputs/metrics/robustness.json")
