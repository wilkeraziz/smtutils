"""
Extracts minimal phrases from symmetrized word alignments
"""


from collections import defaultdict, deque

def try_expand(f, f2e, f_min, f_max, e_min, e_max):
    """
    Try to expand the boundaries of a phrase pair based on the alignment points in f2e[f]
    :param f: a position in the source
    :param f2e: maps source positions into a sorted list of aligned target positions
    :param f_min, f_max: source phrase boundary
    :param e_min, e_max: target phrase boundary
    :returns: f_min, f_max, e_min, e_max, discovered target positions 
    """
    # retrieve the target positions reachable from f
    es = f2e.get(f, None)
    extra = []
    # if there is any
    if es is not None:
        if f_min is None: 
            # we just discovered that we know something about the source phrase
            f_min = f_max = f
        if e_min is None: # thus e_max is also None
            # we just learnt the first thing about the target phrase
            e_min = es[0]
            e_max = es[-1]
            # basically, we discovered the positions [e_min .. e_max]
            extra.extend(xrange(e_min, e_max + 1))
        else:
            # we have the chance to update our target phrase
            if e_min > es[0]:
                # we discovered a few extra words on the left
                extra.extend(xrange(es[0], e_min))
                # and update e_min
                e_min = es[0]
            if e_max < es[-1]: # update e_max
                # we discovered a few extra words to the right
                extra.extend(xrange(e_max + 1, es[-1] + 1))
                # and update e_max
                e_max = es[-1]
    return f_min, f_max, e_min, e_max, extra

def minimal_biphrases(f_words, e_words, links):
    """
    Returns the minimal phrase pairs
    :param f_words: list of source words
    :param e_words: list of target words
    :param links: list of alignment points
    :return: list of tuples (source phrase, target phrase) where a phrase is a list of positions in f_words or e_words
    """
    # 1) organise alignment points
    # first we group them
    f2e = defaultdict(set)
    e2f = defaultdict(set)
    for i, j in links:
        f2e[i].add(j)
        e2f[j].add(i)
    # then we sort them
    f2e = {f:sorted(es) for f, es in f2e.iteritems()}
    e2f = {e:sorted(fs) for e, fs in e2f.iteritems()}
    # biphrases
    biphrases = set()
    # 2) find minimal phrase pairs
    f_done = set()
    e_done = set()
    # iterate investigating words in the source
    # TODO: sort alignment points as to visit adjacent points first
    for fi, ej in links:
        # check if row or column have alread been done, if so, the minimal phrase consistent with this alignment point has already been found
        if fi in f_done or ej in e_done:
            continue
        else:
            # flag row and column as processed
            f_done.add(fi)
            e_done.add(ej)
        # source phrase boundaries
        f_min, f_max = fi, fi
        # target phrase boundaries
        e_min, e_max = ej, ej
        # queue of words whose alignment points need be investigated
        f_queue = deque([f_min])
        e_queue = deque([e_min])
        # for as long as there are words to be visited
        while f_queue or e_queue:
            if f_queue: 
                # get a source word
                f = f_queue.popleft()
                # try to expand the boundaries
                f_min, f_max, e_min, e_max, extra = try_expand(f, f2e, f_min, f_max, e_min, e_max)
                # book discovered target words
                e_queue.extend(extra)
            if e_queue: 
                # get a target word
                e = e_queue.popleft()
                # try to expand the boundaries (the logic is the same, only transposed)
                e_min, e_max, f_min, f_max, extra = try_expand(e, e2f, e_min, e_max, f_min, f_max)
                # book discovered source words
                f_queue.extend(extra)

        # store the minimal phrase
        f_phrase = tuple(range(f_min, f_max + 1))
        e_phrase = tuple(range(e_min, e_max + 1))
        biphrases.add((f_phrase, e_phrase))

    return biphrases

def unaligned_words(f_words, e_words, biphrases):
    """Find unaligned words 
    :param f_words: source words
    :param e_words: target words
    :param biphrases: list of phrase pairs (check `minimal_biphrases`)
    :returns: set of unaligned source words, set of unaligned target words
    """
    fs = set()
    es = set()
    for fp, ep in biphrases:
        fs.update(fp)
        es.update(ep)
    return frozenset(range(len(f_words))) - fs, frozenset(range(len(e_words))) - es

def parse_strings(fstr, estr, astr):
    """
    :param fstr: source string
    :param estr: target string
    :param astr: alingment string
    :return: list of source words, a list of target words and list of alignment points 
        where an alignment point is a pair of integers (i, j)
    """
    f = fstr.split()
    e = estr.split()
    a = [map(int, link.split('-')) for link in astr.split()]
    return f, e, a

def parse_line(line, separator = ' ||| '):
    """returns the source words, the target words and the alignment points"""
    return parse_strings(*line.split(separator))

