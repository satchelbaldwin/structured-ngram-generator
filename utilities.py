import nltk

class TreeBankPCFGrammar:
    def __init__():
        self.symbols_list = []
        self.symbols = frozenset()
        self.rules = {}
        self.build()
    # add a rule if it doesn't exist
    # otherwise, if it does, count that rule
    # towards the probability total for the lhs expression.
    def add_rule(self, rule):
        (lhs, rhs) = rule
        if lhs not in self.rules:
            self.rules[lhs] = {}
            self.rules[lhs]["total_count"] = 1
            self.rules[lhs]["expansions"] = {}
        else:
            self.rules[lhs]["total_count"] = self.rules[lhs]["total_count"] + 1
        # grab a reference to the expansions for ease of use
        expansions = self.rules[lhs]["expansions"]
        # tuples are immutable/hashable unlike lists, so rhs must be a tuple
        if rhs not in expansions:
            expansions[rhs] = {"count" : 1, "probability" : None}
        else:
            expansions[rhs]["count"] = expansions[rhs]["count"] + 1

    def finalize_rule_probabilities(self):
        for lhs, rhs in self.rules:
            rule_data = self.rules[lhs]["expansions"][rhs]
            rule_data["probability"] = rule_data["count"] / self.rules[lhs]["total_count"]

    def get_rules_from_treebank(self):

        pass

    def build(self):
        
