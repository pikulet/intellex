import pickle
from index import Dictionary, PostingList
from Eval import Eval
from PositionalMerge import *

########################### DEFINE CONSTANTS ###########################
CONJUNCTION_OPERATOR = " AND "
PHRASE_MARKER = "\""
INVALID_TERM_IDF = -1

######################## FILE READING FUNCTIONS ########################

### Retrieve a dictionary mapping docIDs to normalised document lengths
###
def get_lengths(p):
    p.seek(0)
    length_dict = pickle.load(p)
    return length_dict

### Retrieve a dictionary format given the dictionary file
###
def get_dictionary(dictionary_file):
    with open(dictionary_file, 'rb') as f:
        dictionary = pickle.load(f)
    return dictionary

### Retrieve a query format given the query file
###
def get_query(query_file):
    with open(query_file, 'r') as f:
        data = f.read().splitlines()

    query = data[0]
    query_text = parse_query(data[0])
    is_boolean = "AND" in query
    positive_list = [int(x) for x in data[1:]]
    return query_text, positive_list, is_boolean

### Retrieve the posting list for a particular term
###
def get_posting(p, dictionary, t):
    try:
        term_data = dictionary[t]
        idf = term_data[Dictionary.IDF]
        
        offset = term_data[Dictionary.TERM_OFFSET]
        p.seek(offset)
        data = pickle.load(p)
        return idf, data
    except KeyError:
        # Term does not exist in dictionary
        return INVALID_TERM_IDF, list()
    
######################## QUERY PROCESSING ########################

### Parse the free-text query for AND operators and phrases (" ")
### "fertility treatment" AND damages --> [ ['fertility', 'treatment'], 'damages']
### AND operator is currently ignored, phrases are grouped together in a list.
###
def parse_query(q):
    q = q.split(CONJUNCTION_OPERATOR)
    is_phrase = lambda s: s.startswith(PHRASE_MARKER)
    parse_phrase = lambda s: s[1: -1].split()

    result = list()
    for t in q:
        if is_phrase(t):
            result.append(parse_phrase(t))
        else:
            result.extend(t.split())
    return result

def process_query(p, dictionary, query):
    '''
    :param p:
    :param dictionary:
    :param query:
    :return:
    '''
    query_terms = query[0]
    positive_list = query[1]
    query_is_boolean = query[2]  # have to look at boolean case
    doc_lengths = get_lengths(p)
    posting_lists = []
    for term in query_terms:
        if type(term) == list: # phrase query
            phrase_postings_lists = list(map(lambda word: get_posting(p, dictionary, word)[1], term))
            posting_list = get_postings_from_phrase(term, phrase_postings_lists)
            dictionary[tuple(term)] = [len(posting_list), 0] # put phrase into dictionary
            ## need to store idf instead, and take care of 0 cases
        else:
            posting_list = get_posting(p, dictionary, term)[1] #(idf, posting_list) pair
        posting_lists.append(posting_list)
    eval = Eval(query_terms, posting_lists, dictionary, doc_lengths, 10000) #need to retrieve num_docs
    print(eval.eval_query())
    return eval.eval_query()