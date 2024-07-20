
# IMPLEMENTATION OF ANGLUIN'S L* ALGORITHM

import itertools
import os
from dfa import DFA

import hydra
import yaml
from omegaconf import DictConfig

# OBSERVATION TABLE CLASS DEFINITION

class ObservationTable:
    """
    Represents the observation table to learn specific DFAs

    Systematically queries the system to discover both states and transitions of the minimal DFA that are 
    representative of accurate learning behavior

    Three main components:
    - S: Set of prefixes observed
    - E: Set of suffixes when appended to prefixes in S determine DFA specific states
    - T: Observation table itself, mapping pairs to outcomes based on membership query

    T is hence iteratively expanded and refined based on responses from Learner until it satisfies the properties
    of being both closed and consistent
    """

    def __init__(self, alphabet):
        self.S = ['']  # Initial set of prefixes
        self.E = ['']  # Initial set of suffixes
        self.T = {}    # Observation table
        self.alphabet = alphabet # Input alphabet for DFA in process

    def fill_table(self, membership_query):
        # Expand the observation table based on S, E, and alphabet
        # Updated to avoid redundant queries
        for s in self.S + [s + a for s in self.S for a in self.alphabet]:
            for e in self.E:
                if (s, e) not in self.T:
                    self.T[(s, e)] = membership_query(s + e)
        self.display_table()

    def is_closed(self):
        # Check if the table is closed
        # Updated to consider extensions not in S
        for s in self.S:
            for a in self.alphabet:
                extended_s = s + a
                if not any(self.get_row(extended_s) == self.get_row(s2) for s2 in self.S):
                    return False, extended_s
        return True, None

    def is_consistent(self):
        # Check if the table is consistent
        for s1 in self.S:
            for s2 in self.S:
                if s1 != s2 and self.get_row(s1) == self.get_row(s2):
                    for a in self.alphabet:
                        if self.get_row(s1 + a) != self.get_row(s2 + a):
                            return False, s1, s2, a
        return True, None, None, None

    def get_row(self, s):
        # Get row from observation table
        return tuple(self.T.get((s, e), False) for e in self.E)

    def add_to_S(self, s):
        # Add prefix to S
        if s not in self.S:
            self.S.append(s)

    def add_to_E(self, e):
        # Add a new suffix to E
        if e not in self.E:
            self.E.append(e)

    def display_table(self):
        # Check current state of observation table
        print("After expansion of observation table:")
        print("S:", self.S)
        print("E:", self.E)
        print("T:", [(k, self.T[k]) for k in sorted(self.T.keys(), key=lambda x: (x[0], x[1]))])


# TEACHER / ORACLE CLASS DEFINITION

class Teacher:
    """
    Performs membership queries to determine if strings belong to the language of the specified target DFA.
    Performs equivalence queries to check if the hypothesis DFA is equivalent to the specified target DFA.
    """

    def __init__(self, target_dfa, depth=20):
        self.target_dfa = target_dfa
        self.depth = depth
        self.membership_query_count = 0
        self.equivalence_query_count = 0

    def membership_query(self, string):
        self.membership_query_count += 1
        return self.target_dfa.accepts(string)

    def equivalence_query(self, hypothesis):
        self.equivalence_query_count += 1
        for depth in range(1, self.depth + 1):
            for string in self.generate_test_strings(depth):
                if self.target_dfa.accepts(string) != hypothesis.accepts(string):
                    print(f"Counterexample found: {string}")
                    return string
        return None

    def generate_test_strings(self, depth, prefix='', alphabet=None):
        if alphabet is None:
            alphabet = self.target_dfa.alphabet
        if depth == 0:
            return [prefix]
        strings = []
        for a in alphabet:
            strings.extend(self.generate_test_strings(depth - 1, prefix + a, alphabet))
        return strings

    def find_counterexample(self, hypothesis_dfa):
        """
        Finds a counterexample for the given hypothesis DFA.
        Returns the counterexample if found, otherwise returns None.
        """
        for input_sequence in self.generate_input_sequences(self.target_dfa.alphabet, self.depth):
            if self.target_dfa.accepts(input_sequence) != hypothesis_dfa.accepts(input_sequence):
                return input_sequence
        return None

    def generate_input_sequences(self, alphabet, max_length):
        for length in range(1, max_length + 1):
            for seq in itertools.product(alphabet, repeat=length):
                yield ''.join(seq)


# L* LEARNER CLASS DEFINITION

class Learner:
    """
    Implementation of L* learning algorithm
    Functions via inference of minimal set DFA to correlate with target DFA

    Learner interacts with Teacher to iteratively refine hypothesis DFA based on both membership and 
    equivalence queries

    Constructs observation table to record direct response and then determines when consistent and closed 
    hypothesis DFA has been detected
    """

    def __init__(self, teacher, alphabet):
        self.teacher = teacher
        self.table = ObservationTable(alphabet)
        self.alphabet = alphabet
        self.previous_counterexamples = set()

    def set_previous_counterexamples(self, counterexamples):
        self.previous_counterexamples = counterexamples

    def learn(self):
        # Execution of L* until hypothesis DFA is equivalent to target DFA
        while True:
            self.table.fill_table(self.teacher.membership_query)
            
            # Check for closure and consistency
            closed, unclosed_s = self.table.is_closed()
            while not closed:
                self.table.add_to_S(unclosed_s)
                self.table.fill_table(self.teacher.membership_query)
                closed, unclosed_s = self.table.is_closed()

            consistent, s1, s2, a = self.table.is_consistent()
            while not consistent:
                self.table.add_to_E(a)
                self.table.fill_table(self.teacher.membership_query)
                consistent, s1, s2, a = self.table.is_consistent()

            # Construct DFA hypothesis and check for equivalence
            hypothesis_dfa = self.construct_dfa()
            counterexample = self.teacher.equivalence_query(hypothesis_dfa)
            if counterexample:
                self.handle_counterexample(counterexample)
            else:
                return hypothesis_dfa

    def construct_dfa(self):
        # Constructs DFA from current state of observation table
        unique_rows = {}
        for s in self.table.S:
            row = self.table.get_row(s)
            if row not in unique_rows:
                unique_rows[row] = "state_" + str(len(unique_rows))

        states = set(unique_rows.values())
        alphabet = self.alphabet
        transition_function = {}
        start_state = unique_rows[self.table.get_row('')]
        accept_states = set()

        for s in self.table.S:
            if self.table.T.get((s, ''), False):
                accept_states.add(unique_rows[self.table.get_row(s)])
        
        for s in self.table.S:
            for a in self.alphabet:
                sa_row = self.table.get_row(s + a)
                if sa_row in unique_rows:
                    transition_function[(unique_rows[self.table.get_row(s)], a)] = unique_rows[sa_row]

        dfa = DFA(states=states, alphabet=alphabet,
                  transition_function=transition_function,
                  start_state=start_state, accept_states=accept_states)
        return dfa

    def handle_counterexample(self, counterexample):
        added = False
        for i in range(1, len(counterexample) + 1):
            prefix = counterexample[:i]
            if prefix not in self.table.S:
                self.table.S.append(prefix)
                added = True
                
        if added:
            self.table.fill_table(self.teacher.membership_query)
            self.check_and_resolve_table_issues()

    def check_and_resolve_table_issues(self):
        closed, unclosed_s = self.table.is_closed()
        while not closed:
            self.table.add_to_S(unclosed_s)
            self.table.fill_table(self.teacher.membership_query)
            closed, unclosed_s = self.table.is_closed()
        
        consistent, s1, s2, a = self.table.is_consistent()
        while not consistent:
            self.table.add_to_E(a)
            self.table.fill_table(self.teacher.membership_query)
            consistent, s1, s2, a = self.table.is_consistent()


def load_dfa_config(dfa_path):
    with open(dfa_path, 'r') as file:
        return yaml.safe_load(file)


def create_dfa(dfa_config):
    try:
        states = set(dfa_config['states'])
        alphabet = set(dfa_config['alphabet'])
        start_state = dfa_config['start_state']
        accept_states = set(dfa_config['accept_states'])
        transitions = {}
        for state, mapping in dfa_config['transitions'].items():
            for symbol, dest in mapping.items():
                transitions[(state, symbol)] = dest
        return DFA(states, alphabet, transitions, start_state, accept_states)
    except Exception as e:
        print(f"Error when creating DFA: {e}")
        raise


@hydra.main(config_path="../conf", config_name="config", version_base="1.1")
def main(cfg: DictConfig):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..'))

        print("Current working directory:", os.getcwd())
        print("Script directory:", script_dir)
        print("Project root:", project_root)
        print("Initialising test DFA")

        # Example: Select DFA1 for testing - modify as needed
        dfa_key = 'dfa1'
        dfa_relative_path = cfg.dfas[dfa_key]
        dfa_full_path = os.path.join(project_root, 'conf', dfa_relative_path)
        print("DFA full path:", dfa_full_path)

        if not os.path.exists(dfa_full_path):
            print(f"Error: The file {dfa_full_path} does not exist")
            return

        test_dfa_config = load_dfa_config(dfa_full_path)
        test_dfa = create_dfa(test_dfa_config)
        print(f"DFA {dfa_key} initialised successfully")

        print("Creating the Teacher with the test DFA")
        teacher = Teacher(test_dfa)
        print("Teacher created successfully")

        print("Creating the Learner mechanism")
        learner = Learner(teacher, list(test_dfa.alphabet))
        print("Learner created successfully")

        print("Starting the learning process")
        learned_dfa = learner.learn()
        print("Learning process completed successfully")

        print("Learned DFA:")
        print("States:", learned_dfa.states)
        print("Alphabet:", learned_dfa.alphabet)
        print("Transition function:", learned_dfa.transition_function)
        print("Start state:", learned_dfa.start_state)
        print("Accept states:", learned_dfa.accept_states)

    except ImportError as e:
        print(f"ImportError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
