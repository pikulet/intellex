import pickle
from index import Dictionary, PostingList
from Eval import Eval
from PositionalMerge import get_postings_from_phrase
from IntersectMerge import get_intersected_posting_lists
from data_helper import *

########################### DEFINE CONSTANTS ###########################
CONJUNCTION_OPERATOR = " AND "
PHRASE_MARKER = "\""
INVALID_TERM_DF = -1


######################## FILE READING FUNCTIONS ########################

### Retrieve a dictionary mapping docIDs to normalised document lengths
###
def get_document_properties(properties_file):
    document_properties = load_data(properties_file)
    return document_properties

### Retrieve a dictionary format given the dictionary file
###
def get_dictionary(dictionary_file):
    dictionary = load_data(dictionary_file)
    return dictionary


### Retrieve the posting list for a particular term
###
def get_posting(dictionary, p, t):
    try:
        term_data = dictionary.terms[t]
        df = term_data[Dictionary.DF]

        offset = term_data[Dictionary.TERM_OFFSET]
        data = load_data_with_handler(p, offset)
        return df, data
    except KeyError:
        # Term does not exist in dictionary
        return INVALID_TERM_DF, list()


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


######################## QUERY PROCESSING ########################

### Parse the free-text query for AND operators and phrases (" ")
### "fertility treatment" AND damages --> [ ['fertility', 'treatment'], 'damages']
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


def get_posting_lists(p, query_terms, dictionary, query_is_boolean):
    posting_lists = []
    for term in query_terms:
        if type(term) == list:  # phrase query
            phrase_postings_lists = list(map(lambda word: get_posting(p, dictionary, word)[1], term))
            posting_list = get_postings_from_phrase(term, phrase_postings_lists)
            posting_list = (len(posting_list), posting_list) # (df, posting_list) pair
            dictionary[tuple(term)] = [len(posting_list), 0]  # put phrase into dictionary
        else:
            posting_list = get_posting(p, dictionary, term)  # (df, posting_list) pair
        posting_lists.append(posting_list)

    empty_lists = list(filter(lambda x: x[0] == 0, posting_lists))  # filter out empty lists
    if query_is_boolean and not empty_lists:
        posting_lists = get_intersected_posting_lists(posting_lists)
    elif query_is_boolean and empty_lists:
        return []
    else:
        posting_lists = list(map(lambda x: x[1], posting_lists))  # remove df
    return posting_lists


def process_query(p, dictionary, document_properties, query):
    '''
    :param p:
    :param dictionary:
    :param document_properties:
    :param query:
    :return:
    '''
    num_docs = dictionary.total_num_documents
    query_terms = query[0]
    positive_list = query[1]
    query_is_boolean = query[2]
    posting_lists = get_posting_lists(p, query_terms, dictionary, query_is_boolean)
    eval = Eval(query_terms, posting_lists, dictionary, document_properties, num_docs)
    return eval.eval_query()
