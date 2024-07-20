# AG REASONING FRAMEWORK

import itertools
import tracemalloc
from angluin import DFA, Learner, Teacher
from adaptive_query_selection import learn_adaptive

# Function to learn the DFA with optional optimisation method
def learn_dfa(teacher, system_alphabet, use_optimisation=None):
    learner = Learner(teacher, system_alphabet)
    previous_counterexamples = set()
    iteration = 0

    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        if use_optimisation == "adaptive":
            dfa = learn_adaptive(learner, teacher)
        else:
            dfa = learner.learn()
        print("Constructed Hypothesis DFA successfully")

        counterexample = teacher.find_counterexample(dfa)
        if not counterexample:
            print("Learning stage complete - Target DFA successfully learned")
            print(f"Total iterations: {iteration}")
            return dfa, iteration, learner.table

        print(f"Counterexample found: {counterexample}")
        if counterexample in previous_counterexamples:
            print("Infinite loop detected: same counterexample found repeatedly.")
            print(f"Total iterations: {iteration}")
            return dfa, iteration, learner.table
        previous_counterexamples.add(counterexample)

        process_counterexample(counterexample, learner.table, teacher.membership_query)

        print(f"After processing counterexample {counterexample}:")
        print(f"S: {learner.table.S}")
        print(f"E: {learner.table.E}")
        print(f"T: {learner.table.T}")

# Function to process a counterexample and update the observation table
def process_counterexample(counterexample, table, membership_query):
    prefixes = [counterexample[:i] for i in range(1, len(counterexample) + 1)]
    for prefix in prefixes:
        if prefix not in table.S:
            table.S.append(prefix)
        for e in table.E:
            if (prefix, e) not in table.T:
                table.T[(prefix, e)] = membership_query(prefix + e)

# ASSUME GUARANTEE CLASS DEFINITION

class AssumeGuarantee:
    """
    Implements the Assume Guarantee reasoning framework to verify system properties 
    against a set of system components using learnt assumptions.
    """

    def __init__(self, system_components, system_alphabet, property_to_verify, search_depth, max_length):
        self.system_components = system_components  # Components of the system
        self.system_alphabet = system_alphabet      # Alphabet of the system
        self.property_to_verify = property_to_verify  # Property DFA to be verified
        self.search_depth = search_depth  # Search depth for equivalence queries
        self.max_length = max_length      # Maximum length for input sequences
        self.assumptions = []             # List to store learnt assumptions

        self.total_iterations = 0         # Total iterations for learning
        self.total_membership_queries = 0 # Total membership queries made
        self.total_equivalence_queries = 0# Total equivalence queries made
        self.hypothesis_dfa_size = 0      # Size of the hypothesis DFA
        self.counterexamples = []         # List to store counterexamples

    # Function to create a Teacher for a given target component
    def create_teacher_for(self, target_component):
        return Teacher(target_dfa=target_component, depth=self.search_depth)

    # Function to verify an individual assumption against a target component
    def verify_individual_assumption(self, assumption_dfa, target_component):
        for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
            target_accepts = target_component.accepts(input_sequence)
            assumption_accepts = assumption_dfa.accepts(input_sequence)
            if target_accepts != assumption_accepts:
                print(f"Assumption verification failed for input {input_sequence}: target={target_accepts}, assumption={assumption_accepts}")
                return False
        print(f"Assumption verification succeeded for all input sequences up to length {self.max_length}.")
        return True

    # Function to generate input sequences of given length from the alphabet
    def generate_input_sequences(self, alphabet, max_length):
        for length in range(1, max_length + 1):
            for seq in itertools.product(alphabet, repeat=length):
                yield ''.join(seq)

    # Function to verify the system property against the system components
    def verify_system_property(self):
        for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
            expected_behavior = all(component.accepts(input_sequence) for component in self.system_components)
            actual_property_response = self.property_to_verify.accepts(input_sequence)
            if actual_property_response != expected_behavior:
                print(f"Property verification failed for input: {input_sequence}, expected: {expected_behavior}, got: {actual_property_response}")
                return False
        return True

    # Function to learn assumptions using an optional optimisation method
    def learn_assumptions(self, optimisation_method=None):
        print("Learning assumptions...")
        for component in self.system_components:
            teacher = self.create_teacher_for(component)
            assumption_dfa, iterations, table = learn_dfa(teacher, self.system_alphabet, optimisation_method)

            self.total_iterations += iterations
            self.total_membership_queries += teacher.membership_query_count
            self.total_equivalence_queries += teacher.equivalence_query_count
            self.hypothesis_dfa_size = len(assumption_dfa.states)
            self.counterexamples.append(teacher.equivalence_query_count)

            if not self.verify_individual_assumption(assumption_dfa, component):
                print(f"Verification failed for component {component}")
                return False

            print(f"Assumption for component {component} learned successfully: {assumption_dfa}")
            print(f"Assumption DFA transitions: {assumption_dfa.transition_function}")

            self.assumptions.append(assumption_dfa)
        return True

    # Function to verify the system with learnt assumptions
    def verify(self, optimisation_method=None):
        if not self.learn_assumptions(optimisation_method):
            return False

        if self.verify_system_property():
            print("System satisfies property under learnt assumptions")
            return True
        else:
            print("System does not satisfy property under learnt assumptions")
            return False

    # Function to verify the system with combined learnt assumptions
    def verify_with_combined_assumptions(self, optimisation_method=None):
        if self.verify(optimisation_method):
            combined_assumption = self.combine_assumptions()
            if combined_assumption and self.verify_system_property_with_combined_assumptions(combined_assumption):
                print("System satisfies property under combined learnt assumptions")
            else:
                print("System does not satisfy property under combined learnt assumptions")

    # Function to combine all learnt assumptions into a single DFA
    def combine_assumptions(self):
        combined_assumption = None
        for assumption in self.assumptions:
            if combined_assumption is None:
                combined_assumption = assumption
            else:
                combined_assumption = combined_assumption.intersect(assumption)
        return combined_assumption

    # Function to verify the system property with combined assumptions
    def verify_system_property_with_combined_assumptions(self, combined_assumption):
        for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
            combined_accepts = combined_assumption.accepts(input_sequence)
            property_accepts = self.property_to_verify.accepts(input_sequence)
            if combined_accepts != property_accepts:
                print(f"Combined assumption verification failed for input {input_sequence}: combined={combined_accepts}, property={property_accepts}")
                return False
        return True

    def verify_without_optimisation(self):
        """
        Regular verification process without optimisation.
        """
        self.total_iterations += 1
        combined_assumption = self.combine_assumptions()
        if combined_assumption and self.verify_system_property_with_combined_assumptions(combined_assumption):
            print("System satisfies property under combined learnt assumptions")
        else:
            print("System does not satisfy property under combined learnt assumptions")
