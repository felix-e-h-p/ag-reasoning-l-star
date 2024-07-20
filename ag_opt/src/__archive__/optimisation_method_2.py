class OptimisationMethod2:
    def __init__(self):
        pass

    def selective_membership_queries(self, ag):
        print("Applying selective membership queries...")
        for state in ag.current_states:
            enabled_actions = ag.get_enabled_actions(state)
            for action in enabled_actions:
                ag.query_membership(state, action)

    def run(self, ag):
        self.selective_membership_queries(ag)
        ag.learn_assumptions()
        ag.verify_with_combined_assumptions()
