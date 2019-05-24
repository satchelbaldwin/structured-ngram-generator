#!/usr/bin/env python3

import nltk
from nltk.corpus import treebank
from random import random

class TreeBankGrammar:
    def __init__(self):
        self.rules = {}
        self.get_rules_from_treebank()
        self.finalize_rule_probabilities()
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
        for lhs, rule in self.rules.items():
            total = rule["total_count"]
            for (rhs, data) in rule["expansions"].items():
                data["probability"] = data["count"] / total

    def traverse_node(self, node):
        rules = []
        finished = False
        nodes = [node]
        while len(nodes) != 0:
            node = nodes[0]
            part_of_speech = node.label()
            child_tags = ()
            for child in node:
                if type(child) == nltk.Tree:
                    child_tags = child_tags + (child.label(),)
                    nodes.append(child)
            if len(child_tags) != 0:
                rule = (part_of_speech, child_tags)
                self.add_rule(rule)
            nodes.remove(node)

    def get_rules_from_treebank(self):
        for sentence in treebank.parsed_sents():
            self.traverse_node(sentence)

    def is_terminal(self, tag):
        return (tag not in self.rules)

    def get_expansion(self, tag):
        accumulator = 0.0
        threshold = random()
        for (rhs, data) in self.rules[tag]["expansions"].items():
            expansion = rhs
            accumulator = accumulator + data["probability"]
            if accumulator >= threshold:
                return expansion

    def expand_first_nonterminal_tag(self, sentence):
        for index in range(0, len(sentence)):
            if not self.is_terminal(sentence[index]):
                tag = sentence.pop(index)
                expansion = self.get_expansion(tag)
                return (sentence[:index] + list(expansion) + sentence[index:])

    def build_sentence(self):
        # for the first sentence, just make sure it starts with *something*
        # and ends with punctuation. after that, all bets are off
        sentence = ["S"]
        while any([not self.is_terminal(s) for s in sentence]):
            sentence = self.expand_first_nonterminal_tag(sentence)
        return sentence

    def __str__(self):
        rules_list = []
        for lhs, rule in self.rules.items():
            for rhs, data in rule["expansions"].items():
                rule_string = "{:<20} -> {:<30} \t[{:<}]".format(
                        lhs, 
                        " ".join(rhs), 
                        data["probability"])
                rules_list.append(rule_string)
        return "\n".join(rules_list)

