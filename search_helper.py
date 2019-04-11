from data_helper import *
from constants import *
from index_helper import Dictionary, PostingList
from properties_helper import COURT_HIERARCHY
from Eval import Eval
from PositionalMerge import get_postings_from_phrase
from IntersectMerge import get_intersected_posting_lists
from query_expander import get_new_query_vector

import heapq

########################### DEFINE CONSTANTS ###########################

MAX_DOCS = 200
CONJUNCTION_OPERATOR = " AND "
PHRASE_MARKER = "\""
INVALID_TERM_DF = -1

######################## FILE READING FUNCTIONS ########################

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

def parse_query(query, dictionary):
    '''
    Parse the free-text non-boolean query for phrases, performing normalisation.
    :param query: a query string
    :return: a list of single word terms with normalisation.
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
    return result

def parse_boolean_query(query, dictionary):
    '''
    Parse the free-text query for AND operators and phrases (" ")
    For example, "fertility treatment" AND damages --> [ ['fertility', 'treatment'], 'damages']
    :param query: a query string
    :return: a list of phrases represented as lists of single words.
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
    return result

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
        dictionary.terms[tuple(phrase)] = [len(posting_list), -1]  # put phrase into dictionary
        posting_lists.append(posting_list)
    return posting_lists

def get_posting_list_intersection(single, biword, triword):
    single = list(map(lambda x: [len(x), x], single))
    biword = list(map(lambda x: [len(x), x], biword))
    triword = list(map(lambda x: [len(x), x], triword))
    reduced_single, reduced_biword, reduced_triword = get_intersected_posting_lists(single, biword, triword)
    return reduced_single, reduced_biword, reduced_triword

def merge_doc_to_score_dicts(dicts, weights):
    score_dict = {}
    for dict_no in range(len(dicts)):
        curr_dict = dicts[dict_no]
        for doc in curr_dict:
            if doc not in score_dict:
                score_dict[doc] = 0
            score_dict[doc] += weights[dict_no] * curr_dict[doc]
    return score_dict

def get_top_scores_from_dict(score_dict):
    doc_score_pairs = list(score_dict.items())
    score_list = list(map(lambda x: (-x[1], x[0]), doc_score_pairs))
    top_results = heapq.nsmallest(MAX_DOCS, score_list, key=lambda x: (x[0], x[1]))  # smallest since min_heap is used
    top_documents = list(map(lambda x: str(x[1]), top_results))
    return top_documents

### deal with one word phrases!!

def process_query(postings_handler, dictionary, doc_properties, query, is_title=False):
    '''
    :param postings_handler:
    :param dictionary:
    :param doc_properties:
    :param query:
    :return:
    '''
    query_terms = list(filter(lambda x: type(x) == list or x in dictionary.terms, query[0])) # remove terms not in dic
    query_is_boolean = query[2]

    single_terms = list(filter(lambda x: type(x) != list, query_terms))
    biwords = list(filter(lambda x: type(x) == list and len(x) == 2, query_terms))
    triwords = list(filter(lambda x: type(x) == list and len(x) == 3, query_terms))

    single_term_plists = get_posting_lists(postings_handler, single_terms, dictionary, query_is_boolean)
    biword_plists = get_phrase_posting_lists(postings_handler, biwords, dictionary, query_is_boolean)
    triword_plists = get_phrase_posting_lists(postings_handler, triwords, dictionary, query_is_boolean)

    if query_is_boolean:
        single_term_plists, biword_plists, triword_plists = get_posting_list_intersection(single_term_plists,
                                                                                          biword_plists, triword_plists)

    single_term_scores = Eval(single_terms, single_term_plists, dictionary, doc_properties, is_title=is_title).eval_query()
    biword_scores = Eval(biwords, biword_plists, dictionary, doc_properties, term_length=2, is_title=is_title).eval_query()
    triword_scores = Eval(triwords, triword_plists, dictionary, doc_properties, term_length=3, is_title=is_title).eval_query()

    score_dict = merge_doc_to_score_dicts([single_term_scores, biword_scores, triword_scores],
                             [SINGLE_TERMS_WEIGHT, BIWORD_PHRASES_WEIGHT, TRIWORD_PHRASES_WEIGHT])
    return score_dict

def get_best_documents(postings_handler, dictionary, doc_properties, query):
    '''
    Returns the top documents based on content, title, courts and dates field.
    :return:
    '''
    content_doc_to_scores = process_query(postings_handler, dictionary, doc_properties, query)
    title_dictionary = load_data(TITLE_DICTIONARY_FILE)
    title_postings = open(TITLE_POSTINGS_FILE, 'rb')
    title_doc_to_scores = process_query(title_postings, title_dictionary, doc_properties, query, is_title=True)

    score_dict = merge_doc_to_score_dicts([content_doc_to_scores, title_doc_to_scores], [CONTENT_WEIGHT, TITLE_WEIGHT])
    ## factor in court and date
    top_docs = get_top_scores_from_dict(score_dict)
    return top_docs

def expand_query(postings_handler, dictionary, doc_properties, query, relevant_docs):
    query_terms = query[0]
    query = list(filter(lambda x: type(x) != list, query_terms))
    eval = Eval(query, [], dictionary, doc_properties)
    terms = eval.get_term_frequencies(query)
    query_vector = eval.get_query_vector(terms)
    terms = list(map(lambda x: x[0], terms))
    query_vector_dic = dict(zip(terms, query_vector))
    relevant_docs = list(map(lambda x: int(x), relevant_docs))
    new_query_vector = list(get_new_query_vector(query_vector_dic, relevant_docs).items())
    terms = list(map(lambda x: x[0], new_query_vector))
    tf_idf = list(map(lambda x: x[1], new_query_vector))
    posting_lists = get_posting_lists(postings_handler, terms, dictionary, query_is_boolean=False)
    new_query_scores = Eval(terms, posting_lists, dictionary, doc_properties, tf_idf).eval_query()
    top_docs = get_top_scores_from_dict(new_query_scores)
    return top_docs

def identify_courts(query_string):
    '''
    Returns courts that exist within a query string.
    :return: 
    '''
    courts = []
    for court in COURT_HIERARCHY:
        if court in query_string:
            courts.append(court)
    return courts