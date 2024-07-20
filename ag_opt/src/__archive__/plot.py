# RUN_AG.PY - MAIN EXECUTION SCRIPT

import time
import tracemalloc
import yaml
import os
from ag_reasoning import AssumeGuarantee
from dfa import DFA
import hydra
from omegaconf import DictConfig
import matplotlib.pyplot as plt

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

def run_ag_reasoning(target_dfa, property_dfa, use_optimisation, search_depth, max_length):
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
    
    # Focus only on DFAs 9, 10, 11, and 12
    selected_dfa_indices = [8, 9, 10, 11]

    all_results_without_optimisation = []
    all_results_with_optimisation = []

    operational_times_without_optimisation = []
    operational_times_with_optimisation = []

    for idx, i in enumerate(selected_dfa_indices):
        target_dfa = target_dfas[i]
        property_dfa = property_dfas[i]
        print(f"\nRunning comparison for DFA {i + 1}...")
        
        results_without_optimisation_runs = []
        results_with_optimisation_runs = []
        times_without_optimisation = []
        times_with_optimisation = []

        for _ in range(num_runs):
            results_without_optimisation = run_ag_reasoning(target_dfa, property_dfa, False, search_depth, max_length)
            results_with_optimisation = run_ag_reasoning(target_dfa, property_dfa, "enhanced", search_depth, max_length)
            
            results_without_optimisation_runs.append(results_without_optimisation)
            results_with_optimisation_runs.append(results_with_optimisation)

            times_without_optimisation.append(results_without_optimisation['time_taken'])
            times_with_optimisation.append(results_with_optimisation['time_taken'])

        avg_results_without_optimisation = average_results(results_without_optimisation_runs)
        avg_results_with_optimisation = average_results(results_with_optimisation_runs)

        all_results_without_optimisation.append(avg_results_without_optimisation)
        all_results_with_optimisation.append(avg_results_with_optimisation)

        operational_times_without_optimisation.append(times_without_optimisation)
        operational_times_with_optimisation.append(times_with_optimisation)

    print("\nSummary of Results:")
    for i, (results_without, results_with) in enumerate(zip(all_results_without_optimisation, all_results_with_optimisation)):
        print(f"\nDFA {selected_dfa_indices[i] + 1}:")
        print(f"Without Optimisation: {results_without}")
        print(f"With Enhanced Hypothesis Merging Optimisation: {results_with}")

    # Plot results for DFAs 9, 10, 11, and 12
    for idx, i in enumerate(selected_dfa_indices):
        plt.figure()
        plt.plot(range(num_runs), operational_times_without_optimisation[idx], label='Without Optimisation', color='blue')
        plt.plot(range(num_runs), operational_times_with_optimisation[idx], label='With Optimisation', color='red')
        plt.xlabel('Run')
        plt.ylabel('Time Taken (s)')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    main()
