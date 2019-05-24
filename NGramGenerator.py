#!/usr/bin/env python3

from TreeBankGrammar import *
from random import random
import nltk, math

# shamelessly stolen from project 3

# only tag starts
def lower_sentences(lines):
    sentences = []
    for line in lines:
        sentence = line.split()
        sentence = [word.lower() for word in sentence]
        sentences.append(sentence)
    return sentences

def get_ngrams(sentences, n):
    #return [i for s in [nltk.ngrams(x, n) for x in sentences] for i in s]
    ngrams = []
    for s in sentences:
        for ngram in nltk.ngrams(s, n):
            ngrams.append(ngram)
    return(ngrams)

def count_ngrams(ngrams):
    ngram_counts = {}
    for ngram in ngrams:
        if ngram not in ngram_counts:
            ngram_counts[ngram] = 1
        else:
            ngram_counts[ngram] = ngram_counts[ngram] + 1
    return ngram_counts

class NGram:
    def __init__(self, count, probability):
        self.count = count
        self.prob = probability
        self.log_prob = math.log(self.prob)
        self.pos = None

class NGramData:
    def __init__(self, n):
        self.n = n
        self.ngrams = {}
    def add(self, name, count, probability):
        self.ngrams[name] = NGram(
                count, 
                probability)
    def pos_tag(self):
        words = map(lambda x: x.split(' ')[-1], list(self.ngrams.keys()))
        tagged = nltk.pos_tag(list(words))
        for (key, (_, tag)) in zip(self.ngrams.keys(), tagged):
            self.ngrams[key].pos = tag

def build_ngram_model(lines):
    sentences = lower_sentences(lines)
    ngram_data = []
    for n in [1, 2]: #[1, 2, 3]:
        ngrams = get_ngrams(sentences, n)
        ngram_counts = count_ngrams(ngrams)

        # conditional frequency is not used with unigrams
        cfd = None
        if n == 2:
            cfd = nltk.ConditionalFreqDist(ngrams)
        if n == 3:
            ngrams_w2 = [ ((n[0], n[1]), n[2]) for n in ngrams ]
            cfd = nltk.ConditionalFreqDist(ngrams_w2)

        data = NGramData(n)
        for ngram in ngrams:
            # unigrams
            count = ngram_counts[ngram]
            if n == 1:
                data.add(' '.join(ngram), count, count / len(ngrams))
            # bigrams
            if n == 2:
                probability = cfd[ngram[0]].freq(ngram[1])
                data.add(' '.join(ngram), count, probability)
            # trigrams
            #if n == 3:
            #    probability = cfd[(ngram[0], ngram[1])].freq(ngram[2])
            #    data.add(' '.join(ngram), count, probability)

        ngram_data.append(data)
    return ngram_data

class NGramGenerator:
    def __init__(self, corpus):
        self.grammar = TreeBankGrammar()
        print("Building NGram Model...")
        self.ngram_model = build_ngram_model(corpus)
        self.unigrams = self.ngram_model[0]
        print("Tagging unigrams...")
        print(self.unigrams.ngrams.items())
        self.unigrams.pos_tag()
        self.bigrams = self.ngram_model[1]
        print("Tagging bigrams...")
        self.bigrams.pos_tag()
        print("Gathering tags...")
        self.accepted_tags = frozenset(
                list([u.pos for _,u in self.unigrams.ngrams.items()]))

    def generate_random(self, valid_keys, data):
        accumulator = 0.0
        scalar = sum([data[k].prob for k in valid_keys])
        threshold = random() * scalar
        for key in valid_keys:
            probability = data[key].prob
            accumulator = accumulator + probability
            if accumulator >= threshold:
                return key
    def generate_unigram(self, tag):
        valid_unigrams = filter(
                lambda k: self.unigrams.ngrams[k].pos == tag,
                self.unigrams.ngrams.keys())
        return self.generate_random(
                list(valid_unigrams), 
                self.unigrams.ngrams)
    def generate_next_word(self, prev, tag):
        # does a word exist that follows this word and is also this tag?
        valid_bigrams = list(
                filter(
                    lambda k: self.bigrams.ngrams[k].pos == tag,
                    filter(
                        lambda k: k.split(' ')[0] == prev,
                        self.bigrams.ngrams.keys())))
        if len(valid_bigrams) != 0:
            return self.generate_random(
                    valid_bigrams, 
                    self.bigrams.ngrams)
        else:
            return self.generate_unigram(tag)
        pass
    def generate_sentence(self):
        # i wish python had a do while construct
        tags = self.grammar.build_sentence()
        tags = list(filter(lambda tag: tag in self.accepted_tags, tags))
        while len(tags) == 0:
            tags = self.grammar.build_sentence()
            tags = list(filter(lambda tag: tag in self.accepted_tags, tags))
        words = [self.generate_unigram(tags.pop(0))]
        for tag in tags:
            words.append(self.generate_next_word(words[-1], tag).split(' ')[-1])
        return words

