import time
import tracemalloc
import yaml
import os
from ag_reasoning import AssumeGuarantee
from dfa import DFA
from optimisation_method_1 import OptimisationMethod1
from optimisation_method_2 import OptimisationMethod2
from optimisation_method_3 import OptimisationMethod3
import hydra
from omegaconf import DictConfig
import matplotlib.pyplot as plt

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
    return DFA(states, alphabet, transitions, start_state, accept_states)

def run_ag_reasoning(target_dfa, property_dfa, optimisation_method, search_depth, max_length):
    system_components = [target_dfa]
    system_alphabet = target_dfa.alphabet
    property_to_verify = property_dfa

    ag = AssumeGuarantee(system_components, system_alphabet, property_to_verify, search_depth, max_length)
    
    optimisation_method.run(ag)
    
    tracemalloc.start()
    start_time = time.time()
    ag.learn_assumptions()
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
    search_depth = cfg.training.search_depth
    max_length = cfg.training.max_length
    num_runs = cfg.training.extend_runs

    target_dfa_path = input("Please enter the path for the target DFA YAML file: ")
    property_dfa_path = input("Please enter the path for the property DFA YAML file: ")

    target_dfa = create_dfa(load_dfa_from_yaml(target_dfa_path))
    property_dfa = create_dfa(load_dfa_from_yaml(property_dfa_path))
    
    all_results_optimisation1 = []
    all_results_optimisation2 = []
    all_results_optimisation3 = []

    optimisations = [
        OptimisationMethod1(),
        OptimisationMethod2(),
        OptimisationMethod3()
    ]

    for optimisation in optimisations:
        results_runs = []
        for _ in range(num_runs):
            results = run_ag_reasoning(target_dfa, property_dfa, optimisation, search_depth, max_length)
            results_runs.append(results)
        avg_results = average_results(results_runs)
        if isinstance(optimisation, OptimisationMethod1):
            all_results_optimisation1.append(avg_results)
        elif isinstance(optimisation, OptimisationMethod2):
            all_results_optimisation2.append(avg_results)
        elif isinstance(optimisation, OptimisationMethod3):
            all_results_optimisation3.append(avg_results)

    print("\nSummary of Results:")
    print(f"\nWith Optimisation Method 1: {all_results_optimisation1}")
    print(f"\nWith Optimisation Method 2: {all_results_optimisation2}")
    print(f"\nWith Optimisation Method 3: {all_results_optimisation3}")

if __name__ == "__main__":
    main()
