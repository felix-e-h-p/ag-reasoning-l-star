
# DFA CLASS DEFINITION

class DFA:
    """
    Specified DFA is defined by a set of states, input alphabet, transition function, start state, and set of 
    acceptance criteria states
    
    Evaluates strings of symbols from alphabet - determines directly whether each string is to be accepted 
    based on its specific transition function
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
