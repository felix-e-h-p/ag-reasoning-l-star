# AG REASONING FRAMEWORK IMPLEMENTATION

import itertools
import tracemalloc
from angluin import DFA, Learner, Teacher
from enhanced_hypothesis_merging import enhanced_hypothesis_merging

def learn_dfa(teacher, system_alphabet):
    """
    Learn DFA using the L* algorithm. Integrates enhanced hypothesis merging for optimisation.
    """
    learner = Learner(teacher, system_alphabet)
    previous_counterexamples = set()
    iteration = 0  # Initialise iteration counter

    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
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

def process_counterexample(counterexample, table, membership_query):
    """
    Process the counterexample by updating the observation table.
    """
    prefixes = [counterexample[:i] for i in range(1, len(counterexample) + 1)]
    for prefix in prefixes:
        if prefix not in table.S:
            table.S.append(prefix)
        for e in table.E:
            if (prefix, e) not in table.T:
                table.T[(prefix, e)] = membership_query(prefix + e)

class AssumeGuarantee:
    """
    Assume-Guarantee reasoning framework to verify system properties using learned assumptions.
    """
    def __init__(self, system_components, system_alphabet, property_to_verify, search_depth, max_length):
        self.system_components = system_components
        self.system_alphabet = system_alphabet
        self.property_to_verify = property_to_verify
        self.search_depth = search_depth
        self.max_length = max_length
        self.assumptions = []

        self.total_iterations = 0
        self.total_membership_queries = 0
        self.total_equivalence_queries = 0
        self.hypothesis_dfa_size = 0
        self.counterexamples = []

    def create_teacher_for(self, target_component):
        """
        Create a teacher for a given system component.
        """
        return Teacher(target_dfa=target_component, depth=self.search_depth)

    def verify_individual_assumption(self, assumption_dfa, target_component):
        """
        Verify if an assumption DFA correctly represents a system component.
        """
        for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
            target_accepts = target_component.accepts(input_sequence)
            assumption_accepts = assumption_dfa.accepts(input_sequence)
            if target_accepts != assumption_accepts:
                print(f"Assumption verification failed for input {input_sequence}: target={target_accepts}, assumption={assumption_accepts}")
                return False
        print(f"Assumption verification succeeded for all input sequences up to length {self.max_length}.")
        return True

    def generate_input_sequences(self, alphabet, max_length):
        """
        Generate all possible input sequences up to a given maximum length.
        """
        for length in range(1, max_length + 1):
            for seq in itertools.product(alphabet, repeat=length):
                yield ''.join(seq)

    def verify_system_property(self):
        """
        Verify if the system property holds true under the current assumptions.
        """
        for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
            expected_behavior = all(component.accepts(input_sequence) for component in self.system_components)
            actual_property_response = self.property_to_verify.accepts(input_sequence)
            if actual_property_response != expected_behavior:
                print(f"Property verification failed for input: {input_sequence}, expected: {expected_behavior}, got: {actual_property_response}")
                return False
        return True

    def learn_assumptions(self):
        """
        Learn assumptions for each system component using the L* algorithm.
        """
        print("Learning assumptions...")
        for component in self.system_components:
            teacher = self.create_teacher_for(component)
            assumption_dfa, iterations, table = learn_dfa(teacher, self.system_alphabet)

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

    def verify(self):
        """
        Verify the system property under the learnt assumptions.
        """
        if not self.learn_assumptions():
            return False

        if self.verify_system_property():
            print("System satisfies property under learnt assumptions")
            return True
        else:
            print("System does not satisfy property under learnt assumptions")
            return False

    def verify_with_combined_assumptions(self):
        """
        Verify the system property under combined assumptions.
        """
        if self.verify():
            combined_assumption = self.combine_assumptions()
            if combined_assumption and self.verify_system_property_with_combined_assumptions(combined_assumption):
                print("System satisfies property under combined learnt assumptions")
            else:
                print("System does not satisfy property under combined learnt assumptions")

    def combine_assumptions(self):
        """
        Combine all learnt assumptions into a single DFA.
        """
        combined_assumption = None
        for assumption in self.assumptions:
            if combined_assumption is None:
                combined_assumption = assumption
            else:
                combined_assumption = combined_assumption.intersect(assumption)
        return combined_assumption

    def verify_system_property_with_combined_assumptions(self, combined_assumption):
        """
        Verify the system property using the combined assumptions DFA.
        """
        for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
            combined_accepts = combined_assumption.accepts(input_sequence)
            property_accepts = self.property_to_verify.accepts(input_sequence)
            if combined_accepts != property_accepts:
                print(f"Combined assumption verification failed for input {input_sequence}: combined={combined_accepts}, property={property_accepts}")
                return False
        return True

    def enhanced_hypothesis_merging(self):
        """
        Apply enhanced hypothesis merging to refine the learnt DFAs.
        """
        print("Starting enhanced hypothesis merging...")
        enhanced_hypothesis_merging(self)

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

