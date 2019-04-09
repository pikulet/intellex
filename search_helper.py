import pickle
from index import Dictionary, PostingList
from Eval import Eval
from PositionalMerge import get_postings_from_phrase
from IntersectMerge import get_intersected_posting_lists
from data_helper import *
from nltk import PorterStemmer
import heapq

########################### DEFINE CONSTANTS ###########################
CONJUNCTION_OPERATOR = " AND "
PHRASE_MARKER = "\""
INVALID_TERM_DF = -1
PORTER_STEMMER = PorterStemmer()

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
def get_posting(postings_handler, dictionary, t):
    try:
        term_data = dictionary.terms[t]
        df = term_data[Dictionary.DF]

        offset = term_data[Dictionary.TERM_OFFSET]
        data = load_data_with_handler(postings_handler, offset)
        return df, data
    except KeyError:
        # Term does not exist in dictionary
        return INVALID_TERM_DF, list()

### Retrieve a query format given the query file
###
def get_query(query_file, dictionary):
    with open(query_file, 'r') as f:
        data = f.read().splitlines()

    query = data[0]
    is_boolean = "AND" in query
    if is_boolean:
        query_text = parse_boolean_query(data[0], dictionary)
    else:
        query_text = parse_query(data[0], dictionary)
    positive_list = [int(x) for x in data[1:]]
    return query_text, positive_list, is_boolean

def normalise_term(term):
    return PORTER_STEMMER.stem(term.lower())

def parse_query(query, dictionary):
    '''
    Parse the free-text non-boolean query for phrases, performing normalisation.
    For example, "fertility treatment" damages --> [ ['fertility', 'treatment'], 'damages']
    :param query: a query string
    :return: a list of terms, with phrases represented as lists of terms
    '''
    query = query.split()
    start_phrase = lambda s: s.startswith(PHRASE_MARKER)
    end_phrase = lambda s: s[-1] == '"'

    result = list()
    phrase = []
    index = 0
    while index < len(query):
        if start_phrase(query[index]):
            phrase_bool = True
            phrase.append(normalise_term(query[index][1:]))
            index += 1
            while phrase_bool:
                if end_phrase(query[index]):
                    phrase.append(normalise_term(query[index][:-1]))
                    result.append(phrase)
                    phrase = []
                    phrase_bool = False
                phrase.append(normalise_term(query[index]))
                index += 1
        else:
            result.append(normalise_term(query[index]))
            index += 1

    final_query = list(filter(lambda term: type(term) == list or term in dictionary.terms, result))
    return final_query

def parse_boolean_query(query, dictionary):
    '''
    Parse the free-text query for AND operators and phrases (" ")
    For example, "fertility treatment" AND damages --> [ ['fertility', 'treatment'], 'damages']
    :param query: a query string
    :return: a list of terms, with phrases represented as lists of terms
    '''
    query = query.split(CONJUNCTION_OPERATOR)
    is_phrase = lambda s: s.startswith(PHRASE_MARKER)
    parse_phrase = lambda s: s[1: -1].split()

    result = list()
    for term in query:
        if is_phrase(term):
            result.append(list(map(lambda x: normalise_term(x), parse_phrase(term))))
        else:
            result.extend(list(map(lambda x: normalise_term(x), term.split())))

    final_query = list(filter(lambda x: type(x) == list or term in dictionary.terms, result))
    return final_query

######################## QUERY PROCESSING ########################

def get_posting_lists(postings_handler, query_terms, dictionary, query_is_boolean):
    '''
    Get posting lists for single terms.
    :param postings_handler:
    :param query_terms:
    :param dictionary:
    :param query_is_boolean:
    :return:
    '''
    posting_lists = []
    for term in query_terms:
        posting_list = get_posting(postings_handler, dictionary, term)[1]
        posting_lists.append(posting_list)
    return posting_lists

def get_phrase_posting_lists(postings_handler, query_terms, dictionary, query_is_boolean):
    '''
    Get posting lists for phrase queries
    :return:
    '''
    posting_lists = []
    for phrase in query_terms:
        phrase_postings_lists = list(map(lambda word: get_posting(postings_handler, dictionary, word)[1], phrase))
        posting_list = get_postings_from_phrase(phrase, phrase_postings_lists)
        dictionary.terms[tuple(phrase)] = [len(posting_list), 0]  # put phrase into dictionary
        posting_lists.append(posting_list)
    return posting_lists

def get_posting_list_intersection(posting_lists):
    posting_lists = list(map(lambda x: [len(x), x], posting_lists))
    #empty_lists = list(filter(lambda x: x[0] == 0, posting_lists))  # filter out empty lists
    #if query_is_boolean and not empty_lists:
    posting_lists = get_intersected_posting_lists(posting_lists)
    #elif query_is_boolean and empty_lists:
    #    return []
    #else:
    #    posting_lists = list(map(lambda x: x[1], posting_lists))  # remove df
    return posting_lists

SINGLE_TERMS_WEIGHT = 1
BIWORD_PHRASES_WEIGHT = 1
TRIWORD_PHRASES_WEIGHT = 1

def process_query(postings_handler, dictionary, document_properties, query):
    '''
    :param postings_handler:
    :param dictionary:
    :param document_properties:
    :param query:
    :return:
    '''
    num_docs = dictionary.total_num_documents
    query_terms = query[0]
    positive_list = query[1]
    query_is_boolean = query[2]

    single_terms = list(filter(lambda x: type(x) != list, query_terms))
    biword_phrases = list(filter(lambda x: type(x) == list and len(x) == 2, query_terms))
    triword_phrases = list(filter(lambda x: type(x) == list and len(x) == 2, query_terms))

    single_term_posting_lists = get_posting_lists(postings_handler, single_terms, dictionary, query_is_boolean)
    biword_posting_lists = get_phrase_posting_lists(postings_handler, biword_phrases, dictionary, query_is_boolean)
    triword_posting_lists = get_phrase_posting_lists(postings_handler, triword_phrases, dictionary, query_is_boolean)

    single_term_scores = Eval(single_terms, single_term_posting_lists, dictionary, document_properties, num_docs).eval_query()
    biword_phrase_scores = Eval(biword_phrases, biword_posting_lists, dictionary, document_properties, num_docs, term_length=2).eval_query()
    triword_phrase_scores = Eval(triword_phrases, triword_posting_lists, dictionary, document_properties, num_docs, term_length=3).eval_query()

    score_dict = {}
    for doc in single_term_scores:
        if doc not in score_dict:
            score_dict[doc] = 0
        score_dict[doc] += SINGLE_TERMS_WEIGHT * single_term_scores[doc]
    for doc in biword_phrase_scores:
        if doc not in score_dict:
            score_dict[doc] = 0
        score_dict[doc] += BIWORD_PHRASES_WEIGHT * biword_phrase_scores[doc]
    for doc in triword_phrase_scores:
        if doc not in score_dict:
            score_dict[doc] = 0
        score_dict[doc] += TRIWORD_PHRASES_WEIGHT * triword_phrase_scores[doc]

    doc_score_pairs = list(score_dict.items())
    score_list = list(map(lambda x: (-x[1], x[0]), doc_score_pairs))
    top_results = heapq.nsmallest(10, score_list, key=lambda x: (x[0], x[1]))  # smallest since min_heap is used
    top_documents = list(map(lambda x: str(x[1]), top_results))
    return top_documents