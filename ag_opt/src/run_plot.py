
import time
import tracemalloc
import yaml
import os
import matplotlib.pyplot as plt
import numpy as np
from ag_reasoning import AssumeGuarantee
from dfa import DFA
import hydra
from omegaconf import DictConfig

def load_dfa_from_yaml(filepath):
    with open(filepath, 'r') as file:
        dfa_config = yaml.safe_load(file)
    return dfa_config

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
    print("Created DFA:")
    print(f"States: {states}")
    print(f"Alphabet: {alphabet}")
    print(f"Start State: {start_state}")
    print(f"Accept States: {accept_states}")
    print(f"Transition Function: {transitions}")
    return DFA(states, alphabet, transitions, start_state, accept_states)

def run_ag_reasoning(target_dfa, property_dfa, optimisation_method, search_depth, max_length, selective_threshold=0.5):
    system_components = [target_dfa]
    system_alphabet = target_dfa.alphabet
    property_to_verify = property_dfa

    ag = AssumeGuarantee(system_components, system_alphabet, property_to_verify, search_depth, max_length)
    
    tracemalloc.start()
    start_time = time.time()
    
    ag.learn_assumptions(optimisation_method=optimisation_method, selective_threshold=selective_threshold)
    ag.verify_with_combined_assumptions(optimisation_method=optimisation_method, selective_threshold=selective_threshold)
    
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
    search_depth = cfg.training.search_depth
    max_length = cfg.training.max_length
    num_runs = cfg.training.extend_runs
    selective_threshold = cfg.training.get("selective_threshold", 0.5)

    target_dfa_path = cfg.dfas.target_dfa
    property_dfa_path = cfg.dfas.property_dfa

    # Ensure the paths are set or prompt the user
    if not target_dfa_path or not os.path.exists(target_dfa_path):
        target_dfa_path = input("Please enter the path for the target DFA YAML file: ").strip()
    if not property_dfa_path or not os.path.exists(property_dfa_path):
        property_dfa_path = input("Please enter the path for the property DFA YAML file: ").strip()

    target_dfa_path = os.path.abspath(target_dfa_path)
    property_dfa_path = os.path.abspath(property_dfa_path)
    
    # Print the absolute paths for debugging
    print(f"Target DFA path: '{target_dfa_path}' (Exists: {os.path.exists(target_dfa_path)})")
    print(f"Property DFA path: '{property_dfa_path}' (Exists: {os.path.exists(property_dfa_path)})")
    
    # Load the DFAs
    if os.path.exists(target_dfa_path) and os.path.exists(property_dfa_path):
        target_dfa = create_dfa(load_dfa_from_yaml(target_dfa_path))
        property_dfa = create_dfa(load_dfa_from_yaml(property_dfa_path))
    else:
        raise FileNotFoundError(f"One or both of the provided DFA files do not exist: {target_dfa_path}, {property_dfa_path}")
    
    all_results_reuse = []
    all_results_selective = []
    all_results_minimised = []

    for _ in range(num_runs):
        results_reuse = run_ag_reasoning(target_dfa, property_dfa, "reuse", search_depth, max_length)
        results_selective = run_ag_reasoning(target_dfa, property_dfa, "selective", search_depth, max_length, selective_threshold)
        results_minimised = run_ag_reasoning(target_dfa, property_dfa, "minimised", search_depth, max_length)
        
        all_results_reuse.append(results_reuse)
        all_results_selective.append(results_selective)
        all_results_minimised.append(results_minimised)

    avg_results_reuse = average_results(all_results_reuse)
    avg_results_selective = average_results(all_results_selective)
    avg_results_minimised = average_results(all_results_minimised)

    print("Summary of Results:")
    print(f"With Counterexample Reuse Optimisation: {avg_results_reuse}")
    print(f"With Selective Membership Query Optimisation: {avg_results_selective}")
    print(f"With Assumption Alphabet Minimisation Optimisation: {avg_results_minimised}")

    # Plotting the results with polynomial regression and logarithmic y-axis
    plt.figure(figsize=(10, 6))

    # Extracting data for plotting
    x = np.arange(1, num_runs + 1)
    y_reuse = np.array([res['time_taken'] for res in all_results_reuse])
    y_selective = np.array([res['time_taken'] for res in all_results_selective])
    y_minimised = np.array([res['time_taken'] for res in all_results_minimised])

    # Fit a polynomial of degree 3 (or any other degree) to the data
    poly_degree = 3
    poly_reuse = np.poly1d(np.polyfit(x, y_reuse, poly_degree))
    poly_selective = np.poly1d(np.polyfit(x, y_selective, poly_degree))
    poly_minimised = np.poly1d(np.polyfit(x, y_minimised, poly_degree))

    # Plot the best fit lines
    plt.plot(x, poly_reuse(x), label='Counterexample Reuse')
    plt.plot(x, poly_selective(x), label='Selective Membership Query')
    plt.plot(x, poly_minimised(x), label='Assumption Alphabet Minimisation')

    # Set logarithmic scale for y-axis
    plt.yscale('log')
    plt.xlabel('Run')
    plt.ylabel('Time Taken (s)')
    plt.legend()
    plt.grid(False)
    plt.show()

if __name__ == "__main__":
    main()
