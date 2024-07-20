# test_ag_reasoning.py
import unittest
from ag_reasoning import AssumeGuarantee, learn_dfa
from angluin import DFA, Learner, Teacher
import yaml
import os

class TestAGReasoning(unittest.TestCase):
    
    def setUp(self):
        """
        Set up the test environment by loading DFA configurations and creating DFA objects.
        """
        # Define a simple DFA configuration for testing
        self.dfa_config = {
            'states': ['q0', 'q1'],
            'alphabet': ['a', 'b'],
            'start_state': 'q0',
            'accept_states': ['q1'],
            'transitions': {
                'q0': {'a': 'q1', 'b': 'q0'},
                'q1': {'a': 'q0', 'b': 'q1'}
            }
        }
        self.dfa = self.create_dfa(self.dfa_config)
        
    def create_dfa(self, dfa_config):
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

    def test_load_dfa_from_yaml(self):
        """
        Test the function to load DFA configuration from a YAML file.
        """
        # Save the DFA configuration to a temporary YAML file
        with open('temp_dfa.yaml', 'w') as file:
            yaml.dump(self.dfa_config, file)
        
        # Load the DFA configuration from the YAML file
        with open('temp_dfa.yaml', 'r') as file:
            loaded_config = yaml.safe_load(file)
        
        # Remove the temporary YAML file
        os.remove('temp_dfa.yaml')
        
        self.assertEqual(self.dfa_config, loaded_config)
        
    def test_create_dfa(self):
        """
        Test the function to create a DFA from the loaded configuration.
        """
        dfa = self.create_dfa(self.dfa_config)
        self.assertEqual(dfa.states, set(self.dfa_config['states']))
        self.assertEqual(dfa.alphabet, set(self.dfa_config['alphabet']))
        self.assertEqual(dfa.start_state, self.dfa_config['start_state'])
        self.assertEqual(dfa.accept_states, set(self.dfa_config['accept_states']))
        self.assertEqual(dfa.transition_function, {
            'q0': {'a': 'q1', 'b': 'q0'},
            'q1': {'a': 'q0', 'b': 'q1'}
        })
        
    def test_assume_guarantee_reasoning(self):
        """
        Test the Assume-Guarantee reasoning process.
        """
        system_components = [self.dfa]
        system_alphabet = self.dfa.alphabet
        property_to_verify = self.dfa
        search_depth = 10
        max_length = 10
        
        ag = AssumeGuarantee(system_components, system_alphabet, property_to_verify, search_depth, max_length)
        
        self.assertTrue(ag.learn_assumptions())
        self.assertTrue(ag.verify())

class TestAngluinLStar(unittest.TestCase):
    
    def setUp(self):
        """
        Set up the test environment for Angluin's L* algorithm.
        """
        # Define a simple DFA configuration for testing
        self.dfa_config = {
            'states': ['q0', 'q1'],
            'alphabet': ['a', 'b'],
            'start_state': 'q0',
            'accept_states': ['q1'],
            'transitions': {
                'q0': {'a': 'q1', 'b': 'q0'},
                'q1': {'a': 'q0', 'b': 'q1'}
            }
        }
        self.dfa = self.create_dfa(self.dfa_config)
        self.teacher = Teacher(self.dfa)

    def create_dfa(self, dfa_config):
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
    
    def test_membership_query(self):
        """
        Test the membership query function of the teacher.
        """
        self.assertTrue(self.teacher.membership_query("a"))
        self.assertFalse(self.teacher.membership_query("b"))

    def test_equivalence_query(self):
        """
        Test the equivalence query function of the teacher.
        """
        # Create a hypothesis DFA that is not equivalent to the target DFA
        hypothesis_dfa_config = {
            'states': ['q0', 'q1'],
            'alphabet': ['a', 'b'],
            'start_state': 'q0',
            'accept_states': ['q0'],
            'transitions': {
                'q0': {'a': 'q1', 'b': 'q0'},
                'q1': {'a': 'q0', 'b': 'q1'}
            }
        }
        hypothesis_dfa = self.create_dfa(hypothesis_dfa_config)
        
        counterexample = self.teacher.find_counterexample(hypothesis_dfa)
        self.assertIsNotNone(counterexample)

    def test_learn_dfa(self):
        """
        Test the learning process of Angluin's L* algorithm.
        """
        system_alphabet = self.dfa.alphabet
        learned_dfa, iterations, table = learn_dfa(self.teacher, system_alphabet)
        
        # Ensure the learned DFA states match the actual DFA states
        expected_states = {'state_' + str(i) for i in range(len(self.dfa.states))}
        self.assertEqual(set(learned_dfa.states), expected_states)

        self.assertEqual(learned_dfa.alphabet, self.dfa.alphabet)
        self.assertEqual(learned_dfa.start_state, 'state_0')
        self.assertEqual(learned_dfa.accept_states, {'state_1'})
        self.assertGreater(iterations, 0)
        self.assertIsNotNone(table)

if __name__ == '__main__':
    unittest.main()
