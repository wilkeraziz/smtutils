#!/usr/bin/env python
"""
A modification of Picaro to extract and display minimal phrases
based on code by Jason Riesa <riesa@isi.edu>
"""

import sys
import argparse
from collections import defaultdict
from functools import partial
from itertools import product
from termcolor import colored
from minphrases import parse_line, minimal_biphrases, unaligned_words


def vertical_print(words, 
        unaligned, 
        out = sys.stdout, 
        bottom_up=False, 
        attach_top=False, 
        filler=' '):
    """
    Prints words vertically side by side
    :param words: sentence
    :param unaligned: set of unaligned positions
    :param out: output stream
    :param bottom_up: if you want the words to read bottom-up
    :param attach_top: if you want the first letter of the word at the top of the screen
    :filler: a char to fill words shorter than the longest word
    """
    if bottom_up:
        words = [w[::-1] for w in words]
    longest_word, longest_len  = max(((w, len(w)) for w in words), key=lambda (w, l): l)
    if attach_top:
        for i in range(longest_len):
            for j, w in enumerate(words):
                if len(w) > i:
                    if j in unaligned:
                        print >> out, colored(w[i], 'red'),
                    else:
                        print >> out, w[i],
                else:
                    print >> out, filler,
            print >> out
    else:
        for i in range(longest_len, 0, -1):
            for j, w in enumerate(words):
                if len(w) < i:
                    print >> out, filler,
                else:
                    if j in unaligned:
                        print >> out, colored(w[(i*-1)], 'red'),
                    else:
                        print >> out, w[(i*-1)],
            print >> out
        
def xpicaro_grid(f_words, 
        e_words, 
        links, 
        biphrases, 
        f_unaligned, 
        e_unaligned, 
        vertical_printer=vertical_print, 
        out = sys.stdout):
    # Initialize alignment objects
    # a holds alignments of user-specified -a1 <file>
    a = defaultdict(lambda: defaultdict(int))     
    
    # Print e_words on the columns
    # First, find the length of the longest word
    vertical_printer(e_words, e_unaligned, out) 

    # fill in mimimal phrases
    if biphrases is not None:
        for fp, ep in biphrases:
            for f, e in product(fp, ep):
                a[f][e] = 3

    # fill in alignment points
    for i, j in links:
        a[i][j] = 1
    
    for i, _ in enumerate(f_words):
        for j, _ in enumerate(e_words):
            link = a.get(i, {}).get(j, 0)
            if link == 0:
                # no link
                print >> out, ':',
            elif link == 1:
                # regular link
                print >>out, u'\u001b[44m\u001b[37m*\u001b[0m',
            elif link == 3:
                # link due to minimal phrase
                print >> out, u'\u001b[44m\u0020\u001b[0m',
        if i in f_unaligned:
            print >> out, colored(f_words[i], 'red')
        else:
            print >> out, f_words[i]
    print >> out


def simply_interactive(args):
    for sid, line in enumerate(args.bitext):
        # add a bit of interaction with the user
        if sid > 0:
            sys.stdout.write("Hit enter to continue or 'q' to quit: ")
            user_input = sys.stdin.readline().strip()
            if user_input.lower() in ["q", "quit"]:
                sys.exit(1)
        # get source and target words and alignment points
        f, e, a = parse_line(line.strip())
        # extract minimal biphrases and unaligned words
        biphrases = minimal_biphrases(f, e, a) 
        uf, ue = unaligned_words(f, e, biphrases)
        print 'sentence=%d' % (sid + 1)
        # print a grid (based on the original Picaro)
        xpicaro_grid(f, 
                e, 
                a,
                biphrases,
                uf,
                ue,
                partial(vertical_print, 
                    bottom_up=args.bottom_up, 
                    attach_top=args.attach_top, 
                    filler=args.filler))

def fully_interactive(args):
    # loads dataset
    corpus = [line.strip() for line in args.bitext]
    sid = 0
    while True:
        sys.stdout.write("Type a sentence id from {0} to {1}, 'n' for next (default), 'p' for previous or 'q' to quit: ".format(1, len(corpus)))
        user_input = sys.stdin.readline().strip()
        try:
            sid = int(user_input)
        except:
            user_input = user_input.lower()
            if user_input == 'p':
                if sid > 0:
                    sid -= 1
            elif user_input == 'q':
                sys.exit(1)
            elif sid <= len(corpus):
                sid += 1
            
        if 1 <= sid <= len(corpus):
            # get source and target words and alignment points
            f, e, a = parse_line(corpus[sid - 1])
            # extract minimal biphrases and unaligned words
            biphrases = minimal_biphrases(f, e, a) 
            uf, ue = unaligned_words(f, e, biphrases)
            # print a grid (based on the original Picaro)
            print 'sentence=%d' % sid
            xpicaro_grid(f, 
                    e, 
                    a,
                    biphrases,
                    uf,
                    ue,
                    partial(vertical_print, 
                        bottom_up=args.bottom_up, 
                        attach_top=args.attach_top, 
                        filler=args.filler))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
            A word-alignment visualization tool based on Picaro (original code by Jason Riesa <riesa@isi.edu>).  
            This version works with already symmetrised alignments.
            It will show alignment points using '*' and the minimal phrase with a change in background color.
            Unaligned words will be shown in red.
            Aligned sentence pairs will be processed one by one, for better navigation use --navigation.
            """,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('bitext', type=argparse.FileType('r'),
            help='aligned bitext with lines formatted as: source string ||| target string ||| alignment string')
    parser.add_argument('--bottom-up', action='store_true',
            help='print vertical words bottom-up')
    parser.add_argument('--attach-top', action='store_true',
            help='attach vertical words to the top of the screen')
    parser.add_argument('--filler', type=str, default=' ',
            help='filler char for vertical printing')
    parser.add_argument('--navigation', action='store_true',
            help='enables full navigation (stores the complete bitext in memory)')
    
    args = parser.parse_args()
    if len(args.filler) > 1:
        raise Exception('filler should be a single char')

    if args.navigation:
        fully_interactive(args)
    else:
        simply_interactive(args)

