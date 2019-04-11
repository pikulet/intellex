from nltk.corpus import wordnet as wn
from data_helper import *

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
    for synset in wn.synsets(t):
        for item in synset.lemma_names():
            terms.append(item)

    return set(filter_terms(terms))

def filter_terms(terms):
    """
    Remove some of the unuseable terms such as _
    """
    return [normalise_term(term) for term in terms if "_" not in term]

if __name__ == "__main__":
    print(thesaurize(["quiet"]))