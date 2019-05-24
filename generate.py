#!/usr/bin/env python3

from NGramGenerator import *
from TreeBankGrammar import *
import sys, pickle

if __name__ == "__main__":
    verb = sys.argv[1]
    if verb == "model":
        corpus = sys.argv[2]
        cfile = open(corpus, 'r')
        outname = sys.argv[3]
        ofile = open(outname, 'wb')

        ng = NGramGenerator(cfile.readlines())
        cfile.close()

        pickle.dump(ng, ofile)
        ofile.close()
    if verb == "sentence":
        pickle_dump = sys.argv[2]
        pickle_file = open(pickle_dump, 'rb')
        ng = pickle.load(pickle_file)
        pickle_file.close()

        ofile = open(sys.argv[3], 'w')
        num = int(sys.argv[4])
        for i in range(0, num):
            print(f"generating sentence {i} of {num}")
            s = ng.generate_sentence()
            print(' '.join(s))
            ofile.write('{}\n'.format(' '.join(s)))

