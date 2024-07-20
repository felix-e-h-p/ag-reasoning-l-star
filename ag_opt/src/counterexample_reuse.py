# COUNTEREXAMPLE REUSE FOR DFA LEARNING

from angluin import Learner

def learn_dfa(teacher, system_alphabet, reuse_counterexamples=False):
    """
    Learns the DFA using the provided teacher and system alphabet
    Optionally reuses counterexamples to improve learning efficiency
    """
    learner = Learner(teacher, system_alphabet)
    previous_counterexamples = set()  # Set to store previously found counterexamples
    iteration = 0

    while True:
        iteration += 1
        dfa = learner.learn()
        counterexample = teacher.find_counterexample(dfa)
        if not counterexample:
            return dfa, iteration, learner.table  # Return the learned DFA if no counterexample is found

        if reuse_counterexamples:
            if counterexample in previous_counterexamples:
                return dfa, iteration, learner.table  # Return if the counterexample was previously encountered
            previous_counterexamples.add(counterexample)

        process_counterexample(counterexample, learner.table, teacher.membership_query)

def process_counterexample(counterexample, table, membership_query):
    """
    Processes the counterexample by updating the observation table
    """
    prefixes = [counterexample[:i] for i in range(1, len(counterexample) + 1)]
    for prefix in prefixes:
        if prefix not in table.S:
            table.S.append(prefix)
            for e in table.E:
                table.T[(prefix, e)] = membership_query(prefix + e)
