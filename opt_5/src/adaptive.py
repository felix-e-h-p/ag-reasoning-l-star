# RUN_AG.PY - MAIN EXECUTION SCRIPT

import time
import tracemalloc
import yaml
import os
from ag_reasoning import AssumeGuarantee
from dfa import DFA
import hydra
from omegaconf import DictConfig

# Function to load DFA configuration from a YAML file
def load_dfa_from_yaml(filepath):
    with open(filepath, 'r') as file:
        dfa_config = yaml.safe_load(file)
    return dfa_config

# Function to create DFA from the loaded configuration
def create_dfa(dfa_config):
    states = set(dfa_config['states'])
    alphabet = set(dfa_config['alphabet'])
    start_state = dfa_config['start_state']
    accept_states = set(dfa_config['accept_states'])
    transitions = {}
    for state, mapping in dfa_config['transitions'].items():
        transitions[state] = {}
        for symbol, dest in mapping.items():
            transitions[state][symbol] = dest
    return DFA(states, alphabet, transitions, start_state, accept_states)

def run_ag_reasoning(target_dfa, property_dfa, use_optimisation, search_depth, max_length, adaptive_learning=False, context_aware=False):
    system_components = [target_dfa]
    system_alphabet = target_dfa.alphabet
    property_to_verify = property_dfa

    ag = AssumeGuarantee(system_components, system_alphabet, property_to_verify, search_depth, max_length)
    
    # Add debugging to check assumptions before optimisation
    print(f"Initial assumptions: {ag.assumptions}")

    # Ensure assumptions are generated
    ag.learn_assumptions()
    print(f"Assumptions after learning: {ag.assumptions}")
    
    tracemalloc.start()
    start_time = time.time()
    if use_optimisation == "enhanced":
        print("Running enhanced hypothesis merging optimisation...")
        ag.enhanced_hypothesis_merging()
    elif adaptive_learning and context_aware:
        print("Running adaptive learning with context-aware adjustments...")
        # Assuming methods adaptive_learning_method and context_aware_adjustments are defined in ag_reasoning.py
        ag.adaptive_learning_method()
        ag.context_aware_adjustments()
    else:
        print("Running verification with combined assumptions...")
        ag.verify_with_combined_assumptions()
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return {
        'iterations': ag.total_iterations,
        'membership_queries': ag.total_membership_queries,
        'equivalence_queries': ag.total_equivalence_queries,
        'dfa_size': ag.hypothesis_dfa_size,
        'counterexamples_count': len(ag.counterexamples),  # Display count of counterexamples
        'time_taken': end_time - start_time,
        'peak_memory': peak / 1024 / 1024
    }

def average_results(results_list):
    avg_results = {}
    num_results = len(results_list)
    for key in results_list[0]:
        avg_results[key] = sum(result[key] for result in results_list) / num_results
    return avg_results

@hydra.main(config_path="../conf", config_name="config", version_base="1.1")
def main(cfg: DictConfig):
    # Load search_depth, max_length, and num_runs from config
    search_depth = cfg.training.search_depth
    max_length = cfg.training.max_length
    num_runs = cfg.training.num_runs

    # Define the paths to the DFA YAML files relative to the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dfa_paths = [os.path.join(project_root, 'conf', cfg.dfas[key]) for key in cfg.dfas]
    
    # Print the absolute paths for debugging
    for path in dfa_paths:
        print(f"Absolute path for {path}: {os.path.abspath(path)}")
    
    # Load the DFAs
    target_dfas = [create_dfa(load_dfa_from_yaml(path)) for path in dfa_paths]
    property_dfas = [create_dfa(load_dfa_from_yaml(path)) for path in dfa_paths]
    
    all_results_without_optimisation = []
    all_results_with_optimisation = []
    all_results_with_adaptive_context_aware = []

    for i, (target_dfa, property_dfa) in enumerate(zip(target_dfas, property_dfas)):
        print(f"\nRunning comparison for DFA {i + 1}...")
        
        results_without_optimisation_runs = []
        results_with_optimisation_runs = []
        results_with_adaptive_context_aware_runs = []

        for _ in range(num_runs):
            results_without_optimisation = run_ag_reasoning(target_dfa, property_dfa, False, search_depth, max_length)
            results_with_optimisation = run_ag_reasoning(target_dfa, property_dfa, "enhanced", search_depth, max_length)
            results_with_adaptive_context_aware = run_ag_reasoning(target_dfa, property_dfa, "enhanced", search_depth, max_length, adaptive_learning=True, context_aware=True)
            
            results_without_optimisation_runs.append(results_without_optimisation)
            results_with_optimisation_runs.append(results_with_optimisation)
            results_with_adaptive_context_aware_runs.append(results_with_adaptive_context_aware)

        avg_results_without_optimisation = average_results(results_without_optimisation_runs)
        avg_results_with_optimisation = average_results(results_with_optimisation_runs)
        avg_results_with_adaptive_context_aware = average_results(results_with_adaptive_context_aware_runs)

        all_results_without_optimisation.append(avg_results_without_optimisation)
        all_results_with_optimisation.append(avg_results_with_optimisation)
        all_results_with_adaptive_context_aware.append(avg_results_with_adaptive_context_aware)

    print("\nSummary of Results:")
    for i, (results_without, results_with, results_adaptive_context) in enumerate(zip(all_results_without_optimisation, all_results_with_optimisation, all_results_with_adaptive_context_aware)):
        print(f"\nDFA {i + 1}:")
        print(f"Without Optimisation: {results_without}")
        print(f"With Enhanced Hypothesis Merging Optimisation: {results_with}")
        print(f"With Adaptive Learning and Context-Aware Adjustments: {results_adaptive_context}")

if __name__ == "__main__":
    main()
