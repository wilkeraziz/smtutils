import sys
import minphrases as mp

# here we read the bilingual corpus (with word alignments) into a list of triples [(F, E, A)]
D = mp.read_corpus(sys.stdin)

for F, E, A in D:  # here we get minimal phrases for each sentence pair
    biphrases = mp.minimal_biphrases(F, E, A)
    # this is just a header
    print '# {0} ||| {1} ||| {2}'.format(' '.join(F), ' '.join(E), ' '.join('{0}-{1}'.format(i, j) for i, j in A))
    # here we print each minimal phrase
    for f, e in biphrases:
        f_phr = mp.as_words(f, F)
        e_phr = mp.as_words(e, E)
        print ' '.join(f_phr), '|||', ' '.join(e_phr)
    # and an empty line, so that we separate the output for each sentence pair
    print

