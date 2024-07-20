class OptimisationMethod1:
    def __init__(self):
        pass

    def reuse_counterexamples(self, ag):
        print("Reusing counterexamples...")
        for counterexample in ag.counterexamples:
            if counterexample in ag.language_recognised:
                ag.refine_with_counterexample(counterexample)

    def run(self, ag):
        self.reuse_counterexamples(ag)
        ag.learn_assumptions()
        ag.verify_with_combined_assumptions()
