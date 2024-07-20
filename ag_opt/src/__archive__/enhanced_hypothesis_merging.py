# ENHANCED HYPOTHESIS MERGING IMPLEMENTATION

from dfa import DFA

def enhanced_hypothesis_merging(instance):
    """
    Enhanced Hypothesis Merging optimisation method.
    """
    if not instance.assumptions:
        print("No assumptions to merge.")
        return

    print("Starting enhanced hypothesis merging...")
    merged_hypotheses = merge_hypotheses(instance)
    success = verify_merged_hypotheses(instance, merged_hypotheses)
    
    if success:
        print("Enhanced hypothesis merging completed successfully.")
    else:
        print("Enhanced hypothesis merging failed.")

def merge_hypotheses(instance):
    """
    Logic to merge hypotheses in an enhanced manner.
    """
    print("Merging hypotheses...")
    merged_hypotheses = []
    for assumption in instance.assumptions:
        merged_hypothesis = merge_component_hypotheses(instance, assumption)
        merged_hypotheses.append(merged_hypothesis)
    print(f"Merged hypotheses: {merged_hypotheses}")
    return merged_hypotheses

def merge_component_hypotheses(instance, assumption):
    """
    Merging logic for a single component's hypotheses.
    """
    print(f"Merging component hypotheses for assumption: {assumption}")
    merged_states = set(assumption.states)
    merged_transitions = {state: {} for state in merged_states}

    for state in assumption.states:
        if state in assumption.transition_function:
            for transition, next_state in assumption.transition_function[state].items():
                if transition not in merged_transitions[state]:
                    merged_transitions[state][transition] = next_state

    merged_hypothesis = DFA(
        states=merged_states,
        alphabet=instance.system_alphabet,
        transition_function=merged_transitions,
        start_state=assumption.start_state,
        accept_states=assumption.accept_states
    )
    print(f"Merged hypothesis: {merged_hypothesis}")
    return merged_hypothesis

def verify_merged_hypotheses(instance, merged_hypotheses):
    """
    Verification process using merged hypotheses.
    """
    print("Verifying merged hypotheses...")
    for hypothesis in merged_hypotheses:
        instance.total_iterations += 1  # Increment the total_iterations counter here
        if not instance.verify_individual_assumption(hypothesis, instance.system_components[0]):
            print("Verification failed for merged hypothesis")
            return False
    print("Verification succeeded for all merged hypotheses.")
    return True
