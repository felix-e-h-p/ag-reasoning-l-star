
# ASSUMPTION ALPHABET MINIMISATION

from angluin import Learner
from dfa import DFA

def minimise_alphabet(assumption_dfa, system_alphabet):
    """
    Minimise the alphabet of the assumption DFA while ensuring it remains correct.
    
    Args:
        assumption_dfa (DFA): The assumption DFA to be minimised.
        system_alphabet (set): The system's alphabet.
    
    Returns:
        DFA: The minimised alphabet DFA.
    """
    print("Initial DFA:")
    print(f"States: {assumption_dfa.states}")
    print(f"Alphabet: {assumption_dfa.alphabet}")
    print(f"Start State: {assumption_dfa.start_state}")
    print(f"Accept States: {assumption_dfa.accept_states}")
    print(f"Transition Function: {assumption_dfa.transition_function}")

    minimised_alphabet = set()
    for symbol in system_alphabet:
        print(f"Checking symbol: {symbol}")
        if affects_acceptance(assumption_dfa, symbol):
            minimised_alphabet.add(symbol)
    
    return create_minimised_dfa(assumption_dfa, minimised_alphabet)

def affects_acceptance(dfa, symbol):
    """
    Check if the symbol affects the acceptance state of the DFA
    """
    initial_acceptance = dfa.accepts('')
    new_dfa = simulate_transition(dfa, symbol)
    new_acceptance = new_dfa.accepts('')
    return initial_acceptance != new_acceptance

def simulate_transition(dfa, symbol):
    """
    Simulate a transition on the DFA and return a new DFA in the new state
    """
    print(f"Simulating transition for state '{dfa.start_state}' with symbol '{symbol}'")
    print(f"Transition function: {dfa.transition_function}")

    if (dfa.start_state, symbol) not in dfa.transition_function:
        print(f"Transition ({dfa.start_state}, '{symbol}') not found in transition function")
        raise KeyError(f"Transition ({dfa.start_state}, '{symbol}') not found in transition function")
    
    new_state = dfa.transition_function[(dfa.start_state, symbol)]
    print(f"New state: {new_state}")
    return DFA(
        dfa.states,
        dfa.alphabet,
        dfa.transition_function,
        new_state,
        dfa.accept_states
    )

def create_minimised_dfa(dfa, minimised_alphabet):
    """
    Create a new DFA with the minimised alphabet.
    
    Args:
        dfa (DFA): The original DFA.
        minimised_alphabet (set): The minimised alphabet.
    
    Returns:
        DFA: The new DFA with the minimised alphabet.
    """
    states = dfa.states
    start_state = dfa.start_state
    accept_states = dfa.accept_states
    transitions = {
        state: {symbol: dfa.transition_function[state, symbol] for symbol in minimised_alphabet if (state, symbol) in dfa.transition_function}
        for state in dfa.states
    }

    print("Minimised DFA:")
    print(f"States: {states}")
    print(f"Alphabet: {minimised_alphabet}")
    print(f"Start State: {start_state}")
    print(f"Accept States: {accept_states}")
    print(f"Transition Function: {transitions}")

    return DFA(states, minimised_alphabet, transitions, start_state, accept_states)

def learn_dfa(teacher, system_alphabet, minimise_alphabet_flag=True):
    """
    Learn a DFA using the given teacher and system alphabet with optional alphabet minimization.
    
    Args:
        teacher (Teacher): The teacher providing membership and equivalence queries.
        system_alphabet (set): The alphabet of the system.
        minimise_alphabet_flag (bool): Whether to minimize the alphabet of the assumption DFA.
    
    Returns:
        DFA: The learned DFA.
        int: The number of iterations.
        ObservationTable: The final observation table.
    """
    learner = Learner(teacher, system_alphabet)
    iteration = 0

    while True:
        iteration += 1
        dfa = learner.learn()
        print(f"Iteration {iteration}: Learned DFA")
        print(f"States: {dfa.states}")
        print(f"Alphabet: {dfa.alphabet}")
        print(f"Start State: {dfa.start_state}")
        print(f"Accept States: {dfa.accept_states}")
        print(f"Transition Function: {dfa.transition_function}")

        counterexample = teacher.find_counterexample(dfa)
        if not counterexample:
            if minimise_alphabet_flag:
                dfa = minimise_alphabet(dfa, system_alphabet)
            return dfa, iteration, learner.table

        process_counterexample(counterexample, learner.table, teacher.membership_query)

def process_counterexample(counterexample, table, membership_query):
    """
    Process the counterexample and update the observation table.
    
    Args:
        counterexample (str): The counterexample string.
        table (ObservationTable): The observation table to update.
        membership_query (function): The membership query function.
    """
    prefixes = [counterexample[:i] for i in range(1, len(counterexample) + 1)]
    for prefix in prefixes:
        if prefix not in table.S:
            table.S.append(prefix)
        for e in table.E:
            if (prefix, e) not in table.T:
                table.T[(prefix, e)] = membership_query(prefix + e)
