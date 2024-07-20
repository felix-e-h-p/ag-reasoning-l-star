from dfa import DFA

def learn_adaptive(learner, teacher):
    """
    Implement adaptive query selection by dynamically selecting queries based on the current state
    and progress of the overall learning process.
    """
    learner.table.S = ['']
    learner.table.E = ['']
    learner.table.T = {}

    while True:
        # Close the observation table
        for s in list(learner.table.S):
            for a in learner.alphabet:
                if s + a not in learner.table.S:
                    learner.table.S.append(s + a)
                    for e in learner.table.E:
                        learner.table.T[(s + a, e)] = teacher.membership_query(s + a + e)

        # Make the observation table consistent
        consistent = True
        for s1 in learner.table.S:
            for s2 in learner.table.S:
                if s1 != s2 and all(learner.table.T.get((s1, e)) == learner.table.T.get((s2, e)) for e in learner.table.E):
                    for a in learner.alphabet:
                        if learner.table.T.get((s1 + a, '')) != learner.table.T.get((s2 + a, '')):
                            learner.table.E.append(a + '')
                            for s in learner.table.S:
                                learner.table.T[(s, a + '')] = teacher.membership_query(s + a + '')
                            consistent = False
                            break
                if not consistent:
                    break
            if not consistent:
                break

        if consistent:
            break

    return make_dfa_from_observation_table(learner.table, learner.alphabet)

def make_dfa_from_observation_table(table, alphabet):
    """
    Constructs the DFA from the observation table.
    """
    states = set(table.S)
    start_state = ''
    accept_states = {s for s in table.S if table.T.get((s, ''), False)}
    transition_function = {}

    for s in table.S:
        for a in alphabet:
            s_prime = s + a
            if s_prime in states:
                transition_function[(s, a)] = s_prime

    return DFA(states=states, alphabet=alphabet, transition_function=transition_function, start_state=start_state, accept_states=accept_states)
