from nltk.corpus import wordnet as wn

def thesaurize(q):
    """
    Given a query q, return a list of lists of unique synonyms for each term t in q.
    """
    # note: this list is not flattened
    results = []
    for t in q:
        results.append(thesaurize_term(t))
    return results
    

def thesaurize_term(t):
    """
    Given a term t, return an ordered list of unique synonyms.
    """
    terms = []
    for s in wn.synsets(t):
        term = s.name().split(".")[0].replace('_',' ')
        if term not in terms:
            terms.append(term)
    return terms
