
# SELECTIVE MEMBERSHIP QUERY

import random
from angluin import Learner

# Function to selectively perform membership queries based on a threshold
def selective_membership_query(query, membership_query, selective_threshold=0.5):

    if random.random() < selective_threshold:
        return membership_query(query)
    else:
        return None  # Skipping the membership query

# Function to learn a DFA using a given teacher and system alphabet with selective membership queries
def learn_dfa(teacher, system_alphabet, selective_threshold=0.5):
    """
    Learn a DFA using the given teacher and system alphabet, utilising selective membership queries
    """
    learner = Learner(teacher, system_alphabet)
    iteration = 0

    while True:
        iteration += 1
        dfa = learner.learn()
        counterexample = teacher.find_counterexample(dfa)
        if not counterexample:
            return dfa, iteration, learner.table

        process_counterexample(counterexample, learner.table, teacher.membership_query, selective_threshold)

# Function to process counterexamples found during learning with selective membership queries
def process_counterexample(counterexample, table, membership_query, selective_threshold):
    """
    Process the counterexample and update the observation table with selective membership queries
    Args:
        counterexample (str): The counterexample string.
        table (ObservationTable): The observation table to update.
        membership_query (function): The membership query function.
        selective_threshold (float): The probability of performing membership queries.
    """
    prefixes = [counterexample[:i] for i in range(1, len(counterexample) + 1)]
    for prefix in prefixes:
        if prefix not in table.S:
            table.S.append(prefix)
            for e in table.E:
                if selective_membership_query(prefix + e, membership_query, selective_threshold) is not None:
                    table.T[(prefix, e)] = membership_query(prefix + e)
