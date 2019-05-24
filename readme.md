# Sentence Generation with N-gram Models Combined with Pre-existing Structures

## Usage

```
generate.py verb arguments...

where verb is:

  generate [corpus] [output]
  ----------------------
    corpus: input file to read from
    output: where to save the generated model

  sentence [model] [output] [number]
  ----------------------------
    model:  a model created by generate
    output: where to save the generated sentences
    number: how many sentences to generate
```

Example usage:

`generate dickens_text.txt dickens_model`  

`generate dickens_model dickens_sentences.txt 10`

## The First Effort

Instead of fitting a model to full sentences in the grammar, this model
attempts to look at part-of-speech trigrams in attempt to generate a
somewhat probablistic grammar that can construct syntactically accurate
sentences more often that trigram generation on its own. For an example,
for the sentence `"the dog chased a cat"`, tagged as follows: `dt nn vbd
dt nn` the rule generation would be as follows:  
trigrams:
- `<s> dt nn`
- `dt nn vbd`
- `nn vbd dt`
- `vbd dt nn`
- `dt nn </s>`

then based on looking at the trigrams, the program would attempt to learn
about phrases through examining different n-gram probabilities.  This is
because `S -> DT NN VBD DT NN | (other example sentences...)` would not be a
useful grammar at all, as it would simply recreate structures from the text
while never generating anything _new_.  We need it to be based on the
structures it learns from, but still create _new_ structures as well.  so,
given that, we need some way to have new structures be introduced.  Once we
have our grammar, we generate sentences by thinking "what word of this tag
is most likely to follow the prior word?" to hopefully pair our generated
list of tags sentence structure to some kind of semantic meaning as well.  

## The Second Effort
While that was my original idea, I quickly ran into trouble with creating
trees for sentences from a given corpus. Identifying general phrase
structures proved to be very difficult. Some approaches considered were
finding large stretches of repeated tag sequences; this did not have the
desired effect I wanted, as the tag sequences-as-phrases were simply just an
abstract stand in for the exact same structures they represented. Other
ideas involved finding similar patterns _around_ a given word; for example,
finding sentences in the format of `[tags] CONJUNCTION [tags]` where the two
surrounding sets of tags around the conjunctions could be considered phrases
that could reoccur in other places. This was very inaccurate for
generation, as the model was much too liberal with how it defined phrases.
Many unrelated tag clusters would be assumed to have the same role. This
pursuit felt like a dead end with my current knowledge of the field.

However, Penn Treebank was extraordinarily useful for getting this base off
the ground.  By creating a grammer from the NLTK sample of the Penn
Treebank, we still have the ability to create new, synthesized sentences
from the model. Here is an example.  Suppose we have the sentences `I
walked.` and `The person walked quickly.`.  A trivial example parse tree for
the first sentence could be `(S (NP (NN "I") VP (VBD "walked")))` and, for
the second `(S (NP (DT "The" NN "person) VP (VBD "walked" JJ "quickly")))`.
So, an example PCFG for this very small corpus could be (barring terminal
symbols, all of which have 1.0 probability in this scenario)  
- `S  -> NP VP  [1.0]`
- `NP -> NN     [0.5]`
- `NP -> DT NN  [0.5]`
- `VP -> VBD    [0.5]`
- `VP -> VBD JJ [0.5]`

Which allows for the generation of `(S (NP (NN) VP (VBD JJ)))`, which, given
our terminal symbols, could generate `I walked quickly`, a structure not
directly seen in this corpus. So, given that this still allows for synthesis
between structures better than simply randomly picking and outright just
reusing a structure found elsewhere, I decided to go with this approach.

## The Implementation

The overall process and goal still remained. In essence, the idea was to
first generate a sentence's structure through generating a sequence of part
of speech tags from a parse tree made from a probablistic context free
grammar. After that, the words of the sentence would be populated through
looking at bigrams in the sense of "given that a word of this tag would
follow the previous word, which word fits the best?" This approach is
designed to combat the pitfall of purely n-gram probability models in that
words make sense with their preceding word but care for nothing of the
context outside of that; that is, sentences should be syntactically correct
(or close most of the time) by using the parse tree, and somewhat
semantically accurate given that the tagged words use context; e.g., if a
past-tense verb followed a noun, the verb would need to be used with that
noun prior in the corpus, hopefully introducing semantic accuracy to some
degree. In this way, phrases should be more accurate and congruent, even if
the overall sentence still has mixed ideas.
  
The first step is to traverse sentences from NLTK's tagged subset of the
Penn Treebank and to scrape rules from each level of the tree of each
sentence. For example, if a sentence has the tree `(S (NP (NN)) (VP
(VBD)))`, rules can be made by seeing each node's direct children. For
example, `S` can go to `NP` and `VP` directly after; hence the rule `S -> VP
NP` being added. Similarly, `NP -> NN` and `VP -> VBD` could be added. Then,
these would be weighted and given probabilities based on the frequencies of
the constructs over the whole treebank.
  
The second step is to generate a sentence structure from tags based on the
PCFG made earlier. Given a sentence, determine the next rule by generating a
random number between `0 and 1.0` and deciding the rule that falls in that
range. Randomly picking rules by the PCFG creates the list of tags used by
the ngram generator after.
  
When generating with ngrams, the model used was bigram generation given the
prior tag. For example, given that the precending word was "The" and the
following word is of type "NN", the generator would pick the word by
probablistic method from ngrams in the corpus restricting to only searching
through words of tag "NN". If the tag generator generates word and tag pairs
that do not exist in the corpus, the generator will prioritize preserving
the tag sequence; it will choose a unigram that fits the tag bu the same
probablistic method. This continues until the sentence is formed.

## Discussion

Penn TreeBank has some crazy rules in the grammar. Unfortunately, this makes
the supposedly syntactically correct sentences still come out sounding
really weird and unnatural. Not only that, the NLTK part of speech tagger
has some slight quirks that make it clash with the Penn TreeBank tags; for
example, the NLTK tagger never tags anything as `NNPS` (plural proper noun),
but the Penn TreeBank has some sentences that expect that tag. Also the NLTK
part of speech tagger tags some non-word symbols oddly; for example,
punctuation gets tagged as a noun. Stripping this could possibly be useful
in the future. Other than that, many of the results seem in line with other
ngram generation models.

## Results and Conclusion

Here is a random sample of sentences generated from Pride and Prejudice by
Jane Austen.
  
`him frequently?” depended on something`  
`satisfactions the house, whichever as myself. to see anything about.`  
`or the _most_ amusing. had which the _most_ amusing. is remarkably fine, collins not`  
`got three miles,`  
`to become a value for she to hear,`  
`be disregarded? hate me.” was truth in one or a monosyllable. do insist give pleasure most heartily to those rites`  
`“i _do_ “i have to attack is in hopes proposed girls they thought, times she grieved “yes; and obliging. the vestibule into most delightfully`  
`thought “i _do_`  
`“but people takes should to explaining to yourself.`  
`_that_ will delivered journey, into the matter--to gentlemen`  
  
From what I can tell, this model has significant limitations that might make
it less suitable for text generation for most cases than simple ngram
generation. The reason for this is that many corpuses I have tried with this
model do not have adequate amounts of material to cover many odd cases of
tags that occur together. For example, the Penn TreeBank sentences
frequently have the construct of `NNP NNP NNP`. Presumably, this is first,
middle, and last names, or something like a corporation's name, or a name
like New York City. Most books I have tried this with struggle to fit to
this, given how infrequently all three of a given character's names are used
back to back. Many constructs like this hinder generation and make
ill-fitting sections much more common than I had anticipated.  

# Inspirations and Referenced Papers
https://dc.uwm.edu/cgi/viewcontent.cgi?article=2063&context=etd  
https://www.aclweb.org/anthology/O06-1004  
"Automatic Learning of Context-Free Grammar", by Chen, Tseng, and Chen
