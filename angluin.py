
# IMPLEMENTATION OF THE L* ALGORITHM
# BASIS OF A-G REASONING FUNCTIONALITY DEFINITIONS

# OBSERVATION TABLE CLASS DEFINITION

class ObservationTable:
    """
    Represents the observation table to learn specific DFAs

    Systematically queries the system to discover both states and transitionsof the minimal DFA that is 
    representative of learning behavior

    Three main components:
    - S: Set of prefixes observed
    - E: Set of suffixes when appended to prefixes in S determine DFA specific states
    - T: Observation table itself, mapping pairs to outcomes based on membership query

    T is iteratively expanded and refined based on responses from Learner until it satisfies the properties
    of being both closed and consistent
    """

    def __init__(self, alphabet):
        self.S = ['']  # Initial set of prefixes
        self.E = ['']  # Initial set of suffixes
        self.T = {}    # Observation table
        self.alphabet = alphabet # Input alphabet for DFA in process

    # def fill_table(self, membership_query):
    #     # Expand the observation table based on S, E, and alphabet
    #     for s in self.S + [s + a for s in self.S for a in self.alphabet]:
    #         for e in self.E:
    #             self.T[(s, e)] = membership_query(s + e)
    #     self.display_table()

    def fill_table(self, membership_query):
        # Expand the observation table based on S, E, and alphabet
        # Updated to avoid redundant queries
        for s in self.S + [s + a for s in self.S for a in self.alphabet]:
            for e in self.E:
                if (s, e) not in self.T:
                    self.T[(s, e)] = membership_query(s + e)
        self.display_table()

    # def is_closed(self):
    #     # Check if the table is closed
    #     for s in self.S:
    #         for a in self.alphabet:
    #             if not any(self.get_row(s + a) == self.get_row(s2) for s2 in self.S):
    #                 return False, s + a
    #     return True, None

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


# DFA CLASS DEFINITION

class DFA:
    """
    DFA is defined by a set of states, an input alphabet, a transition function, a start state, and set of 
    acceptance criteria states
    
    Evaluates strings of symbols from alphabet - determinins directly whether each string is to be accepted 
    based on its transition function
    """

    def __init__(self, states, alphabet, transition_function, start_state, accept_states):
        self.states = states # Set of DFA states
        self.alphabet = alphabet # Input alphabet of DFA
        self.transition_function = transition_function # DFA transition function
        self.start_state = start_state # Start state of evaluation
        self.accept_states = accept_states # Acceptance state of evaluation

    def accepts(self, string):
        # Determinant phase whethere or not DFA accepts a given input string
        current_state = self.start_state
        for symbol in string:
            current_state = self.transition_function.get((current_state, symbol))
            if current_state is None:
                return False
        return current_state in self.accept_states

    def intersect(self, other):
        # Intersection of multiple DFAs - new transition function specified
        new_states = {(s1, s2) for s1 in self.states for s2 in other.states}
        new_start_state = (self.start_state, other.start_state)
        new_accept_states = {(s1, s2) for s1 in self.accept_states for s2 in other.accept_states}
        new_transition_function = {}

        for (s1, s2) in new_states:
            for a in self.alphabet:
                if a in other.alphabet:
                    new_s1 = self.transition_function.get((s1, a))
                    new_s2 = other.transition_function.get((s2, a))
                    if new_s1 is not None and new_s2 is not None:
                        new_transition_function[((s1, s2), a)] = (new_s1, new_s2)

        return DFA(states=new_states,
            alphabet=self.alphabet.intersection(other.alphabet),
            transition_function=new_transition_function,
            start_state=new_start_state,
            accept_states=new_accept_states)

# TEACHER / ORACLE CLASS DEFINITION

class Teacher:
    """
    Performs membership queries to determine if strings belong to language of specified target DFA
    Performs equivalence queries to check if hypothesis DFA is equivalent to specified target DFA
    """

    def __init__(self, target_dfa, depth=20):
        self.target_dfa = target_dfa # Specified target DFA for overall learning process
        self.depth = depth # Maximum depth for generating test strings for equivalence queries - default as 20

    def membership_query(self, string):
        # Checks if the target DFA accepts a given string
        return self.target_dfa.accepts(string)

    def equivalence_query(self, hypothesis):
        # Compares hypothesis DFA to target DFA to obtain counterexample
        for depth in range(1, self.depth + 1):
            for string in self.generate_test_strings(depth):
                if self.target_dfa.accepts(string) != hypothesis.accepts(string):
                    return string
        return None

    def generate_test_strings(self, depth, prefix='', alphabet=None):
        # Recursive generation of test strings to max depth
        if alphabet is None:
            alphabet = self.target_dfa.alphabet
        if depth == 0:
            return [prefix]
        strings = []
        for a in alphabet:
            strings.extend(self.generate_test_strings(depth - 1, prefix + a, alphabet))
        return strings


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
        self.teacher = teacher # Instance of Teacher class
        self.table = ObservationTable(alphabet) # Instance of ObservationTable class
        self.alphabet = alphabet # Input alphabet DFA in process

    def learn(self):
        # Execution of L* until hypothesis DFA is equivalent to target DFA
        while True:
            self.table.fill_table(self.teacher.membership_query)
            
            # Check for closure and consistency
            closed, unclosed_s = self.table.is_closed()
            while not closed:
                print(f"Table not closed with unclosed string: {unclosed_s}")
                self.table.add_to_S(unclosed_s)
                self.table.fill_table(self.teacher.membership_query)
                closed, unclosed_s = self.table.is_closed()

            consistent, s1, s2, a = self.table.is_consistent()
            while not consistent:
                print(f"Table not consistent for: s1={s1}, s2={s2}, with distinguishing suffix: {a}")
                self.table.add_to_E(a)
                self.table.fill_table(self.teacher.membership_query)
                consistent, s1, s2, a = self.table.is_consistent()

            # Construct DFA hypothesis and check for equivalence
            # Ensure a DFA object is always returned
            hypothesis_dfa = self.construct_dfa()
            print("Constructed Hypothesis DFA succesfully")
            counterexample = self.teacher.equivalence_query(hypothesis_dfa)
            if counterexample:
                print(f"Counterexample found: {counterexample}")
                self.handle_counterexample(counterexample)
            else:
                print("Learning stage complete - Target DFA successfully learned")
                return hypothesis_dfa

        # Fallback return IF loop exits unexpectedly
        print("Falling back to default DFA due to unexpected loop exit")
        return DFA(states=set(), alphabet=self.alphabet, transition_function={}, start_state='', accept_states=set())

    def construct_dfa(self):
        # Constructs DFA from current state of observation table
        # Mapping of observation table rows to states
        unique_rows = {}
        for s in self.table.S:
            row = self.table.get_row(s)
            if row not in unique_rows:
                unique_rows[row] = "state_" + str(len(unique_rows))

        # Initialisation of DFA components
        states = set(unique_rows.values())
        alphabet = self.alphabet
        transition_function = {}
        start_state = unique_rows[self.table.get_row('')]
        accept_states = set()

        # Defining accept states based on the observation table
        # Checks if state will be accepted
        for s in self.table.S:
            if self.table.T.get((s, ''), False):
                accept_states.add(unique_rows[self.table.get_row(s)])
        
        # Construction of state transition function
        for s in self.table.S:
            for a in self.alphabet:
                sa_row = self.table.get_row(s + a)
                if sa_row in unique_rows:
                    transition_function[(unique_rows[self.table.get_row(s)], a)] = unique_rows[sa_row]

        # Construct and hence return DFA
        dfa = DFA(states=states, alphabet=alphabet,
                  transition_function=transition_function,
                  start_state=start_state, accept_states=accept_states)
        return dfa

    def make_conjecture(self):
        # Processes counterexample to hence refine observation table
        # Constructs hypothesis DFA and checks for equivalence with target DFA
        dfa = self.construct_dfa()
        print("Constructed Hypothesis DFA:", dfa)
        counterexample = self.teacher.equivalence_query(dfa)
        if counterexample:
            print(f"Counterexample found: {counterexample}")
            self.handle_counterexample(counterexample)
            return False
        else:
            print("No counterexample found - Hypothesis may be correct")
            return True

    def handle_counterexample(self, counterexample):
        added = False

        # Add counterexample prefixes to S if not already present
        print(f"Processing counterexample: {counterexample}")
        for i in range(1, len(counterexample) + 1):
            prefix = counterexample[:i]
            if prefix not in self.table.S:
                print(f"Adding prefix to S: {prefix}")
                self.table.S.append(prefix)
                added = True
                
        # Re-fill table after updating it
        if added:
            self.table.fill_table(self.teacher.membership_query)
            self.check_and_resolve_table_issues()

    def check_and_resolve_table_issues(self):
        closed, unclosed_s = self.table.is_closed()
        while not closed:
            print(f"Table not closed with unclosed string: {unclosed_s}")
            self.table.add_to_S(unclosed_s)
            self.table.fill_table(self.teacher.membership_query)
            closed, unclosed_s = self.table.is_closed()
        
        consistent, s1, s2, a = self.table.is_consistent()
        while not consistent:
            print(f"Table not consistent for: s1={s1}, s2={s2}, with distinguishing suffix: {a}")
            self.table.add_to_E(a)
            self.table.fill_table(self.teacher.membership_query)
            consistent, s1, s2, a = self.table.is_consistent()
