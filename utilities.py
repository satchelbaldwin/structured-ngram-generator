

# possibly move this explanation to a new file instead of comments.
#
# with inspiration from https://www.aclweb.org/anthology/O06-1004
# "Automatic Learning of Context-Free Grammar", by Chen, Tseng, and Chen
#
# instead of fitting a model to full sentences in the grammar, this
# class attempts to look at part-of-speech trigrams in attempt to
# generate a somewhat probablistic grammar that can construct
# syntactically accurate sentences more often that trigram generation
# on its own.
#
# for an example, for the sentence
# "the dog chased a  cat", tagged as follows:
#  dt  nn  vbd    dt nn
# the rule generation would be as follows:
#
# trigrams:
# <s> dt nn
# dt nn vbd
# nn vbd dt
# vbd dt nn
# dt nn </s>
#
# then based on looking at the trigrams, the program would attempt to learn
# about phrases through examining different n-gram probabilities.
#
# this is because S -> DT NN VBD DT NN | (other example sentences...)
# would not be a useful grammar at all, as it would simply recreate
# structures from the text while never generating anything _new_.
#
# we need it to be based on the structures it learns from, but still create
# _new_ structures as well.
#
# so, given that, we need some way to have new structures be introduced.
#
# once we have our grammar, we generate sentences by thinking
# "what word of this tag is most likely to follow the prior word?"
# to hopefully pair our generated list of tags sentence structure
# to some kind of semantic meaning as well.
#
# - - -
# inspiration from here vv
# https://dc.uwm.edu/cgi/viewcontent.cgi?article=2063&context=etd
# while that was my original idea
#
#

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
        
