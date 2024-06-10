
# MAIN SCIPT TO IMPLEMENT L* BASED A-G REASONING FUNCTIONALITY

import itertools
from angluin import DFA, Learner, Teacher
from config import *

# A-G REASONING CLASS DEFINITION

class AssumeGuarantee:
    """
    Implementation of A-G Reasoning utilising L* learning algorithm for system verification purposes 
    Facilitates learning of assumptions regarding individual system components
    Verifies whether entire system satisfies a given property based on learnt assumptions
    
    Four main components:
    - List of system component DFAs to be verified
    - Set of all symbols that can be accepted by systems components
    - DFA representing the property that the system must satisfy
    - Assumptions learnt for each component during verification procedure
    """

    def __init__(self, system_components, system_alphabet, property_to_verify, search_depth, max_length):
        self.system_components = system_components
        self.system_alphabet = system_alphabet
        self.property_to_verify = property_to_verify
        self.search_depth = search_depth
        self.max_length = max_length
        self.assumptions = []

    def create_teacher_for(self, target_component):
        # Instantiates a Teacher based object for any given target component
        return Teacher(target_dfa=target_component, depth=self.search_depth)

    def verify_individual_assumption(self, assumption_dfa, target_component):
        # Verifies learnt assumption DFA represents behavior of target component
        for input_sequence in self.generate_input_sequences(self.system_alphabet):
            if target_component.accepts(input_sequence) != assumption_dfa.accepts(input_sequence):
                return False
        return True

    def generate_input_sequences(self, alphabet):
        # Generates all possible input sequences of specified maximum length of system alphabet
        return [''.join(seq) for seq in itertools.product(alphabet, repeat=self.max_length)]

    # SINGULAR APPROACH - VERIFY LEARNT COMPONENT SEQUENTIALLY

    def verify_system_property(self):
        #
        for input_sequence in self.generate_input_sequences(self.system_alphabet):
            expected_behavior = all(component.accepts(input_sequence) for component in self.system_components)
            actual_property_response = self.property_to_verify.accepts(input_sequence)
            if actual_property_response != expected_behavior:
                print(f"Property verification failed for input: {input_sequence}, expected: {expected_behavior}, got: {actual_property_response}")
                return False
        return True

    def verify(self):
        # Verifies if entire system satisfies testing property relating to learnt assumptions
        all_assumptions_valid = True
        for i, target_component in enumerate(self.system_components):
            print(f"Learning assumption for component {i} based on DFA context")
            teacher = self.create_teacher_for(target_component)
            learner = Learner(teacher, self.system_alphabet)
            assumption_dfa = learner.learn()

            if assumption_dfa is None:
                print("Failed to learn DFA; using a fallback.")
                # Consider enhancing fallback DFA based on expected behavior
                assumption_dfa = DFA(states=set(), alphabet=self.system_alphabet, transition_function={}, start_state='', accept_states=set())

            print(f"Assumption for component {i} learned successfully")
            self.assumptions.append(assumption_dfa)

            if not self.verify_individual_assumption(assumption_dfa, target_component):
                all_assumptions_valid = False
                print(f"Verification failed for component {i}")
                break

        if all_assumptions_valid and self.verify_system_property():
            print("System satisfies property under learnt assumptions")
        else:
            print("System does not satisfy property under learnt assumptions")

    # UPDATE FOR COMBINED APPROACH - NOT SURE WHETHER TO PERSUE OR NOT AT THIS STAGE ???

    def combine_assumptions(self):
        # Combine multiple assumptions utilising intersect from DFA class
        combined_assumption = None
        for assumption in self.assumptions:
            if combined_assumption is None:
                combined_assumption = assumption
            else:
                combined_assumption = combined_assumption.intersect(assumption)
        return combined_assumption

    def verify_system_property_with_combined_assumptions(self, combined_assumption):
        return self.property_to_verify.is_subset_of(combined_assumption)

    def verify_with_combined_assumptions(self):
        # Learn individual assumptions for each component and then combine
        self.verify()        
        combined_assumption = self.combine_assumptions()
        if combined_assumption and self.verify_system_property_with_combined_assumptions(combined_assumption):
            print("System satisfies property under combined learnt assumptions")
        else:
            print("System does not satisfy property under combined learnt assumptions")


# INITIAL OPTIMISATION METHOD - COUNTEREXAMPLE REUSE

# class CounterexampleOptimiser:
#     def __init__(self, learner):
#         self.learner = learner

#     def handle_counterexample(self, counterexample):
#         self.process_substring(counterexample)
#         for i in range(1, len(counterexample)):
#             substring = counterexample[:i]
#             self.process_substring(substring)

#     def process_substring(self, substring):
#         table = self.learner.table
#         alphabet = self.learner.alphabet
#         if substring not in table.S:
#             table.add_to_S(substring)
#             table.fill_table(self.learner.teacher.membership_query)
#         for a in alphabet:
#             extended_substring = substring + a
#             if extended_substring not in table.S:
#                 table.add_to_S(extended_substring)
#                 table.fill_table(self.learner.teacher.membership_query)
