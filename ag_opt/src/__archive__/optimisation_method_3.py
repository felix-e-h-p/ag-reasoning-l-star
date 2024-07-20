class OptimisationMethod3:
    def __init__(self):
        pass

    def minimise_assumption_alphabet(self, ag):
        print("Minimising assumption alphabet...")
        ag.assumption_alphabet = ag.refine_alphabet(ag.original_alphabet)

    def run(self, ag):
        self.minimise_assumption_alphabet(ag)
        ag.learn_assumptions()
        ag.verify_with_combined_assumptions()
