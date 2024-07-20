# AG REASONING FRAMEWORK - RUN

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
    """
    Load the DFA configuration from a YAML file.

    Args:
        filepath (str): Path to the YAML file.

    Returns:
        dict: The DFA configuration.
    """
    with open(filepath, 'r') as file:
        dfa_config = yaml.safe_load(file)
    return dfa_config

# Function to create DFA from the loaded configuration
def create_dfa(dfa_config):
    """
    Create a DFA from the loaded configuration.

    Args:
        dfa_config (dict): The DFA configuration.

    Returns:
        DFA: The created DFA object.
    """
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

def run_ag_reasoning(target_dfa, property_dfa, search_depth, max_length):
    """
    Run the Assume-Guarantee reasoning process.

    Args:
        target_dfa (DFA): The target DFA.
        property_dfa (DFA): The property DFA to verify.
        search_depth (int): The search depth for counterexamples.
        max_length (int): The maximum length of input sequences.

    Returns:
        dict: The results of the reasoning process, including iterations, membership queries, equivalence queries, DFA size, counterexamples count, time taken, and peak memory usage.
    """
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
    """
    Calculate the average results from a list of result dictionaries.

    Args:
        results_list (list): A list of result dictionaries.

    Returns:
        dict: A dictionary of averaged results.
    """
    avg_results = {}
    num_results = len(results_list)
    for key in results_list[0]:
        avg_results[key] = sum(result[key] for result in results_list) / num_results
    return avg_results

@hydra.main(config_path="../conf", config_name="config", version_base="1.1")
def main(cfg: DictConfig):
    """
    Main function to run the AG reasoning process.

    Args:
        cfg (DictConfig): The configuration dictionary.
    """
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
    
    all_results = []

    for i, (target_dfa, property_dfa) in enumerate(zip(target_dfas, property_dfas)):
        print(f"\nRunning comparison for DFA {i + 1}...")
        
        results_runs = []

        for _ in range(num_runs):
            results = run_ag_reasoning(target_dfa, property_dfa, search_depth, max_length)
            results_runs.append(results)

        avg_results = average_results(results_runs)

        all_results.append(avg_results)

    print("\nSummary of Results:")
    for i, results in enumerate(all_results):
        print(f"\nDFA {i + 1}:")
        print(f"Results: {results}")

if __name__ == "__main__":
    main()
