# # AG REASONING FRAMEWORK

# import itertools
# import tracemalloc
# from angluin import DFA, Learner, Teacher
# from counterexample_reuse import learn_dfa as learn_dfa_reuse

# def learn_dfa(teacher, system_alphabet):
#     # Initialises the learner and previous counterexamples
#     learner = Learner(teacher, system_alphabet)
#     previous_counterexamples = set()
#     iteration = 0

#     while True:
#         # Iteratively learns the DFA
#         iteration += 1
#         dfa = learner.learn()
#         counterexample = teacher.find_counterexample(dfa)
#         if not counterexample:
#             return dfa, iteration, learner.table

#         process_counterexample(counterexample, learner.table, teacher.membership_query)

# def process_counterexample(counterexample, table, membership_query):
#     # Processes counterexamples by updating the observation table
#     prefixes = [counterexample[:i] for i in range(1, len(counterexample) + 1)]
#     for prefix in prefixes:
#         if prefix not in table.S:
#             table.S.append(prefix)
#         for e in table.E:
#             if (prefix, e) not in table.T:
#                 table.T[(prefix, e)] = membership_query(prefix + e)

# # ASSUME GUARANTEE CLASS DEFINITION

# class AssumeGuarantee:
#     """
#     Implements Assume-Guarantee reasoning framework to verify system properties.
#     """

#     def __init__(self, system_components, system_alphabet, property_to_verify, search_depth, max_length):
#         # Initialise system components, alphabet, property to verify, search depth, and max length
#         self.system_components = system_components
#         self.system_alphabet = system_alphabet
#         self.property_to_verify = property_to_verify
#         self.search_depth = search_depth
#         self.max_length = max_length
#         self.assumptions = []

#         self.total_iterations = 0
#         self.total_membership_queries = 0
#         self.total_equivalence_queries = 0
#         self.hypothesis_dfa_size = 0
#         self.counterexamples = []

#     def create_teacher_for(self, target_component):
#         # Creates a teacher for a given target component
#         return Teacher(target_dfa=target_component, depth=self.search_depth)

#     def verify_individual_assumption(self, assumption_dfa, target_component):
#         # Verifies if an individual assumption DFA is correct for a given component
#         for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
#             target_accepts = target_component.accepts(input_sequence)
#             assumption_accepts = assumption_dfa.accepts(input_sequence)
#             if target_accepts != assumption_accepts:
#                 print(f"Assumption verification failed for input {input_sequence}: target={target_accepts}, assumption={assumption_accepts}")
#                 return False
#         print(f"Assumption verification succeeded for all input sequences up to length {self.max_length}.")
#         return True

#     def generate_input_sequences(self, alphabet, max_length):
#         # Generates input sequences up to a given maximum length
#         for length in range(1, max_length + 1):
#             for seq in itertools.product(alphabet, repeat=length):
#                 yield ''.join(seq)

#     def verify_system_property(self):
#         # Verifies if the overall system property is satisfied
#         for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
#             expected_behaviour = all(component.accepts(input_sequence) for component in self.system_components)
#             actual_property_response = self.property_to_verify.accepts(input_sequence)
#             if actual_property_response != expected_behaviour:
#                 print(f"Property verification failed for input: {input_sequence}, expected: {expected_behaviour}, got: {actual_property_response}")
#                 return False
#         return True

#     def learn_assumptions(self, reuse_counterexamples=False):
#         # Learns assumptions for the system components
#         print("Learning assumptions...")
#         for component in self.system_components:
#             teacher = self.create_teacher_for(component)
#             if reuse_counterexamples:
#                 assumption_dfa, iterations, table = learn_dfa_reuse(teacher, self.system_alphabet, reuse_counterexamples)
#             else:
#                 assumption_dfa, iterations, table = learn_dfa(teacher, self.system_alphabet)

#             self.total_iterations += iterations
#             self.total_membership_queries += teacher.membership_query_count
#             self.total_equivalence_queries += teacher.equivalence_query_count
#             self.hypothesis_dfa_size = len(assumption_dfa.states)
#             self.counterexamples.append(teacher.equivalence_query_count)

#             if not self.verify_individual_assumption(assumption_dfa, component):
#                 print(f"Verification failed for component {component}")
#                 return False

#             print(f"Assumption for component {component} learned successfully: {assumption_dfa}")
#             print(f"Assumption DFA transitions: {assumption_dfa.transition_function}")

#             self.assumptions.append(assumption_dfa)
#         return True

#     def verify(self, reuse_counterexamples=False):
#         # Verifies the system using the learned assumptions
#         if not self.learn_assumptions(reuse_counterexamples):
#             return False

#         if self.verify_system_property():
#             print("System satisfies property under learnt assumptions")
#             return True
#         else:
#             print("System does not satisfy property under learnt assumptions")
#             return False

#     def verify_with_combined_assumptions(self, reuse_counterexamples=False):
#         # Verifies the system with combined assumptions
#         if self.verify(reuse_counterexamples):
#             combined_assumption = self.combine_assumptions()
#             if combined_assumption and self.verify_system_property_with_combined_assumptions(combined_assumption):
#                 print("System satisfies property under combined learnt assumptions")
#             else:
#                 print("System does not satisfy property under combined learnt assumptions")

#     def combine_assumptions(self):
#         # Combines individual assumptions into a single DFA
#         combined_assumption = None
#         for assumption in self.assumptions:
#             if combined_assumption is None:
#                 combined_assumption = assumption
#             else:
#                 combined_assumption = combined_assumption.intersect(assumption)
#         return combined_assumption

#     def verify_system_property_with_combined_assumptions(self, combined_assumption):
#         # Verifies the system property using the combined assumptions DFA
#         for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
#             combined_accepts = combined_assumption.accepts(input_sequence)
#             property_accepts = self.property_to_verify.accepts(input_sequence)
#             if combined_accepts != property_accepts:
#                 print(f"Combined assumption verification failed for input {input_sequence}: combined={combined_accepts}, property={property_accepts}")
#                 return False
#         return True

#     def verify_without_optimisation(self):
#         # Regular verification process without optimisation
#         self.total_iterations += 1
#         combined_assumption = self.combine_assumptions()
#         if combined_assumption and self.verify_system_property_with_combined_assumptions(combined_assumption):
#             print("System satisfies property under combined learnt assumptions")
#         else:
#             print("System does not satisfy property under combined learnt assumptions")

# # AG REASONING FRAMEWORK

# import itertools
# import tracemalloc
# from angluin import DFA, Learner, Teacher
# from counterexample_reuse import learn_dfa as learn_dfa_reuse
# from selective_membership_query import learn_dfa as learn_dfa_selective

# def learn_dfa(teacher, system_alphabet):
#     # Initialises the learner and previous counterexamples
#     learner = Learner(teacher, system_alphabet)
#     previous_counterexamples = set()
#     iteration = 0

#     while True:
#         # Iteratively learns the DFA
#         iteration += 1
#         dfa = learner.learn()
#         counterexample = teacher.find_counterexample(dfa)
#         if not counterexample:
#             return dfa, iteration, learner.table

#         process_counterexample(counterexample, learner.table, teacher.membership_query)

# def process_counterexample(counterexample, table, membership_query):
#     # Processes counterexamples by updating the observation table
#     prefixes = [counterexample[:i] for i in range(1, len(counterexample) + 1)]
#     for prefix in prefixes:
#         if prefix not in table.S:
#             table.S.append(prefix)
#         for e in table.E:
#             if (prefix, e) not in table.T:
#                 table.T[(prefix, e)] = membership_query(prefix + e)

# class AssumeGuarantee:
#     """
#     Implements Assume-Guarantee reasoning framework to verify system properties.
#     """

#     def __init__(self, system_components, system_alphabet, property_to_verify, search_depth, max_length):
#         # Initialise system components, alphabet, property to verify, search depth, and max length
#         self.system_components = system_components
#         self.system_alphabet = system_alphabet
#         self.property_to_verify = property_to_verify
#         self.search_depth = search_depth
#         self.max_length = max_length
#         self.assumptions = []

#         self.total_iterations = 0
#         self.total_membership_queries = 0
#         self.total_equivalence_queries = 0
#         self.hypothesis_dfa_size = 0
#         self.counterexamples = []

#     def create_teacher_for(self, target_component):
#         # Creates a teacher for a given target component
#         return Teacher(target_dfa=target_component, depth=self.search_depth)

#     def verify_individual_assumption(self, assumption_dfa, target_component):
#         # Verifies if an individual assumption DFA is correct for a given component
#         for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
#             target_accepts = target_component.accepts(input_sequence)
#             assumption_accepts = assumption_dfa.accepts(input_sequence)
#             if target_accepts != assumption_accepts:
#                 print(f"Assumption verification failed for input {input_sequence}: target={target_accepts}, assumption={assumption_accepts}")
#                 return False
#         print(f"Assumption verification succeeded for all input sequences up to length {self.max_length}.")
#         return True

#     def generate_input_sequences(self, alphabet, max_length):
#         # Generates input sequences up to a given maximum length
#         for length in range(1, max_length + 1):
#             for seq in itertools.product(alphabet, repeat=length):
#                 yield ''.join(seq)

#     def verify_system_property(self):
#         # Verifies if the overall system property is satisfied
#         for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
#             expected_behaviour = all(component.accepts(input_sequence) for component in self.system_components)
#             actual_property_response = self.property_to_verify.accepts(input_sequence)
#             if actual_property_response != expected_behaviour:
#                 print(f"Property verification failed for input: {input_sequence}, expected: {expected_behaviour}, got: {actual_property_response}")
#                 return False
#         return True

#     def learn_assumptions(self, optimisation_method="reuse", selective_threshold=0.5):
#         # Learns assumptions for the system components
#         print("Learning assumptions...")
#         for component in self.system_components:
#             teacher = self.create_teacher_for(component)
#             if optimisation_method == "reuse":
#                 assumption_dfa, iterations, table = learn_dfa_reuse(teacher, self.system_alphabet)
#             elif optimisation_method == "selective":
#                 assumption_dfa, iterations, table = learn_dfa_selective(teacher, self.system_alphabet, selective_threshold)
#             else:
#                 assumption_dfa, iterations, table = learn_dfa(teacher, self.system_alphabet)

#             self.total_iterations += iterations
#             self.total_membership_queries += teacher.membership_query_count
#             self.total_equivalence_queries += teacher.equivalence_query_count
#             self.hypothesis_dfa_size = len(assumption_dfa.states)
#             self.counterexamples.append(teacher.equivalence_query_count)

#             if not self.verify_individual_assumption(assumption_dfa, component):
#                 print(f"Verification failed for component {component}")
#                 return False

#             print(f"Assumption for component {component} learned successfully: {assumption_dfa}")
#             print(f"Assumption DFA transitions: {assumption_dfa.transition_function}")

#             self.assumptions.append(assumption_dfa)
#         return True

#     def verify(self, optimisation_method="reuse", selective_threshold=0.5):
#         # Verifies the system using the learned assumptions
#         if not self.learn_assumptions(optimisation_method, selective_threshold):
#             return False

#         if self.verify_system_property():
#             print("System satisfies property under learnt assumptions")
#             return True
#         else:
#             print("System does not satisfy property under learnt assumptions")
#             return False

#     def verify_with_combined_assumptions(self, optimisation_method="reuse", selective_threshold=0.5):
#         # Verifies the system with combined assumptions
#         if self.verify(optimisation_method, selective_threshold):
#             combined_assumption = self.combine_assumptions()
#             if combined_assumption and self.verify_system_property_with_combined_assumptions(combined_assumption):
#                 print("System satisfies property under combined learnt assumptions")
#             else:
#                 print("System does not satisfy property under combined learnt assumptions")

#     def combine_assumptions(self):
#         # Combines individual assumptions into a single DFA
#         combined_assumption = None
#         for assumption in self.assumptions:
#             if combined_assumption is None:
#                 combined_assumption = assumption
#             else:
#                 combined_assumption = combined_assumption.intersect(assumption)
#         return combined_assumption

#     def verify_system_property_with_combined_assumptions(self, combined_assumption):
#         # Verifies the system property using the combined assumptions DFA
#         for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
#             combined_accepts = combined_assumption.accepts(input_sequence)
#             property_accepts = self.property_to_verify.accepts(input_sequence)
#             if combined_accepts != property_accepts:
#                 print(f"Combined assumption verification failed for input {input_sequence}: combined={combined_accepts}, property={property_accepts}")
#                 return False
#         return True

#     def verify_without_optimisation(self):
#         # Regular verification process without optimisation
#         self.total_iterations += 1
#         combined_assumption = self.combine_assumptions()
#         if combined_assumption and self.verify_system_property_with_combined_assumptions(combined_assumption):
#             print("System satisfies property under combined learnt assumptions")
#         else:
#             print("System does not satisfy property under combined learnt assumptions")

# AG REASONING FRAMEWORK

import itertools
import tracemalloc
from angluin import DFA, Learner, Teacher
from counterexample_reuse import learn_dfa as learn_dfa_reuse
from selective_membership_query import learn_dfa as learn_dfa_selective
from assumption_alphabet_minimisation import learn_dfa as learn_dfa_minimised

def learn_dfa(teacher, system_alphabet):
    # Initialises the learner and previous counterexamples
    learner = Learner(teacher, system_alphabet)
    previous_counterexamples = set()
    iteration = 0

    while True:
        # Iteratively learns the DFA
        iteration += 1
        dfa = learner.learn()
        counterexample = teacher.find_counterexample(dfa)
        if not counterexample:
            return dfa, iteration, learner.table

        process_counterexample(counterexample, learner.table, teacher.membership_query)

def process_counterexample(counterexample, table, membership_query):
    # Processes counterexamples by updating the observation table
    prefixes = [counterexample[:i] for i in range(1, len(counterexample) + 1)]
    for prefix in prefixes:
        if prefix not in table.S:
            table.S.append(prefix)
        for e in table.E:
            if (prefix, e) not in table.T:
                table.T[(prefix, e)] = membership_query(prefix + e)

class AssumeGuarantee:
    """
    Implements Assume-Guarantee reasoning framework to verify system properties.
    """

    def __init__(self, system_components, system_alphabet, property_to_verify, search_depth, max_length):
        # Initialise system components, alphabet, property to verify, search depth, and max length
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
        # Creates a teacher for a given target component
        return Teacher(target_dfa=target_component, depth=self.search_depth)

    def verify_individual_assumption(self, assumption_dfa, target_component):
        # Verifies if an individual assumption DFA is correct for a given component
        for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
            target_accepts = target_component.accepts(input_sequence)
            assumption_accepts = assumption_dfa.accepts(input_sequence)
            if target_accepts != assumption_accepts:
                print(f"Assumption verification failed for input {input_sequence}: target={target_accepts}, assumption={assumption_accepts}")
                return False
        print(f"Assumption verification succeeded for all input sequences up to length {self.max_length}.")
        return True

    def generate_input_sequences(self, alphabet, max_length):
        # Generates input sequences up to a given maximum length
        for length in range(1, max_length + 1):
            for seq in itertools.product(alphabet, repeat=length):
                yield ''.join(seq)

    def verify_system_property(self):
        # Verifies if the overall system property is satisfied
        for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
            expected_behaviour = all(component.accepts(input_sequence) for component in self.system_components)
            actual_property_response = self.property_to_verify.accepts(input_sequence)
            if actual_property_response != expected_behaviour:
                print(f"Property verification failed for input: {input_sequence}, expected: {expected_behaviour}, got: {actual_property_response}")
                return False
        return True

    def learn_assumptions(self, optimisation_method="reuse", selective_threshold=0.5):
        # Learns assumptions for the system components
        print("Learning assumptions...")
        for component in self.system_components:
            teacher = self.create_teacher_for(component)
            if optimisation_method == "reuse":
                assumption_dfa, iterations, table = learn_dfa_reuse(teacher, self.system_alphabet)
            elif optimisation_method == "selective":
                assumption_dfa, iterations, table = learn_dfa_selective(teacher, self.system_alphabet, selective_threshold)
            elif optimisation_method == "minimised":
                assumption_dfa, iterations, table = learn_dfa_minimised(teacher, self.system_alphabet)
            else:
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

    def verify(self, optimisation_method="reuse", selective_threshold=0.5):
        # Verifies the system using the learned assumptions
        if not self.learn_assumptions(optimisation_method, selective_threshold):
            return False

        if self.verify_system_property():
            print("System satisfies property under learnt assumptions")
            return True
        else:
            print("System does not satisfy property under learnt assumptions")
            return False

    def verify_with_combined_assumptions(self, optimisation_method="reuse", selective_threshold=0.5):
        # Verifies the system with combined assumptions
        if self.verify(optimisation_method, selective_threshold):
            combined_assumption = self.combine_assumptions()
            if combined_assumption and self.verify_system_property_with_combined_assumptions(combined_assumption):
                print("System satisfies property under combined learnt assumptions")
            else:
                print("System does not satisfy property under combined learnt assumptions")

    def combine_assumptions(self):
        # Combines individual assumptions into a single DFA
        combined_assumption = None
        for assumption in self.assumptions:
            if combined_assumption is None:
                combined_assumption = assumption
            else:
                combined_assumption = combined_assumption.intersect(assumption)
        return combined_assumption

    def verify_system_property_with_combined_assumptions(self, combined_assumption):
        # Verifies the system property using the combined assumptions DFA
        for input_sequence in self.generate_input_sequences(self.system_alphabet, self.max_length):
            combined_accepts = combined_assumption.accepts(input_sequence)
            property_accepts = self.property_to_verify.accepts(input_sequence)
            if combined_accepts != property_accepts:
                print(f"Combined assumption verification failed for input {input_sequence}: combined={combined_accepts}, property={property_accepts}")
                return False
        return True

    def verify_without_optimisation(self):
        # Regular verification process without optimisation
        self.total_iterations += 1
        combined_assumption = self.combine_assumptions()
        if combined_assumption and self.verify_system_property_with_combined_assumptions(combined_assumption):
            print("System satisfies property under combined learnt assumptions")
        else:
            print("System does not satisfy property under combined learnt assumptions")
