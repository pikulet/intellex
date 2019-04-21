from data_helper import *
from constants import *
from Dictionary import Dictionary
from Eval import Eval, get_term_frequencies
from PositionalMerge import get_postings_from_phrase
from BooleanMerge import get_intersected_posting_lists
from QueryExpansion import get_new_query_vector, tokenize, normalise_all_tokens_in_list
import heapq

"""
The main functions in this file are get_best_documents and relevance_feedback.
"""

########################### DEFINE CONSTANTS ###########################

MAX_DOCS = 100000
CONJUNCTION_OPERATOR = " AND "
PHRASE_MARKER = "\""
INVALID_TERM_DF = -1

def get_posting(postings_handler, dictionary, term):
    '''
    Retrieves the posting lists for a particular term. Each posting is
    a list of three items: the docID, the term frequency, and a position list of the term in the document.
    :param postings_handler: a handler to access the postings list file.
    :param dictionary: the dictionary mapping terms to pointers to each posting list in the postings handler.
    :param term: the term
    '''
    try:
        term_data = dictionary[term]
        df = term_data[Dictionary.DF]

        offset = term_data[Dictionary.TERM_OFFSET]
        data = load_data_with_handler(postings_handler, offset)
        return df, data
    except KeyError:
        # Term does not exist in dictionary
        return INVALID_TERM_DF, list()

def get_query(query):
    '''
    Parses a query string into a list of terms, where a term is either a single word string,
    or another list of terms when it is a phrase. Normalisation is also performed on each term.
    For example, "fertility treatment" AND damages is parsed into [['fertil', 'treatment'], 'damag'].
    The parse_query and parse_boolean_query functions are used to parse non-boolean and boolean queries.
    '''
    is_boolean = CONJUNCTION_OPERATOR in query
    if is_boolean:
        query_text = parse_boolean_query(query)
    else:
        query_text = parse_query(query)
    return query_text, is_boolean

def parse_query(query):
    '''
    Parse the free-text non-boolean query for phrases, performing normalisation. For example,
    "fertility treatment" damages is parsed into [['fertil', 'treatment'], 'damag'].
    :param query: a query string.
    '''
    is_boolean, has_phrase, tokenised_query = tokenize(query)
    query = normalise_all_tokens_in_list(tokenised_query)
    if has_phrase:
        query_terms = list(map(lambda x: x.split() if " " in x else x, query))
    else:
        query_terms = query
    for index in range(len(query_terms)):
        if type(query_terms[index]) == list:
            query_terms[index] = list(map(lambda x: normalise_term(x), query_terms[index]))
        else:
            query_terms[index] = normalise_term(query_terms[index])
    return query_terms

def parse_boolean_query(query):
    '''
    Parses a boolean query string using the "AND" operator as a delimiter.
    For example, "fertility treatment" AND damages is parsed into [['fertil', 'treatment'], 'damag']\
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

def get_posting_lists(postings_handler, query_terms, dictionary):
    '''
    Retrieves posting lists for single terms. Returns a list of postings lists.
    :param postings_handler: a handler to access the postings list file.
    :param query_terms: a list of single word terms.
    :param dictionary: the dictionary mapping terms to pointers to each posting list in the postings handler.
    '''
    posting_lists = []
    for term in query_terms:
        term = term[0]
        posting_list = get_posting(postings_handler, dictionary, term)[1]
        posting_lists.append(posting_list)
    return posting_lists

def get_phrase_posting_lists(postings_handler, query_terms, dictionary):
    '''
    Retrieves posting lists for phrase queries. For each phrase, the postings list for each word in the phrase
    is retrieved. The postings lists are intersected using the get_postings_from_phrase function. The phrase
    is then appended to the dictionary with the length of the posting list as its document frequency.
    :param postings_handler: a handler to access the postings list file.
    :param query_terms: a list of single word terms.
    :param dictionary: the dictionary mapping terms to pointers to each posting list in the postings handler.
    '''
    posting_lists = []
    for phrase in query_terms:
        phrase = phrase[0]
        phrase_postings_lists = list(map(lambda word: get_posting(postings_handler, dictionary, word)[1], phrase))
        posting_list = get_postings_from_phrase(phrase, phrase_postings_lists)
        dictionary[tuple(phrase)] = [len(posting_list), -1]  # put phrase into dictionary
        posting_lists.append(posting_list)
    return posting_lists

def merge_doc_to_score_dicts(dicts, weights):
    '''
    Helper function to merge dictionaries mapping documents to cosine scores, weighted.
    For example, if the weight given to biword phrases is twice that of single words,
    the final merged dictionary will reflect this by multiplying each score by the weights
    in the weights list.
    :param dicts: dictionaries to be merged, in the same order as their respective weights in weights.
    :param weights: a list of weights put on the terms from each dictionary.
    '''
    score_dict = {}
    for dict_no in range(len(dicts)):
        curr_dict = dicts[dict_no]
        for doc in curr_dict:
            if doc not in score_dict:
                score_dict[doc] = 0
            score_dict[doc] += weights[dict_no] * curr_dict[doc]
    return score_dict

def get_best_documents(postings_handler, dictionary, doc_properties, query, is_boolean):
    '''
    This function runs search on the top documents based on the content and title fields separately, and then
    combines the cosine scores returned from the searches using some linear weights.
    The second round of search on only the title is done only if CONTENT_ONLY is false.
    In the final submission, search on the title only was omitted as we were unable to learn the appropriate weights
    on each field. Search was thus done on the title and content combined without separation.
    :param postings_handler: a handler to access the postings list file.
    :param dictionary: the dictionary mapping terms to pointers to each posting list in the postings handler.
    :param doc_properties: the dictionary mapping documents to various properties such as document vector length.
    :param query: a list of terms, which can either be single words or phrases stored as lists.
    :param is_boolean: true if the query is boolean.
    '''
    if CONTENT_ONLY:
        content_doc_to_scores = process_query(postings_handler, dictionary, doc_properties, query, is_boolean, is_title=False)
        return get_top_scores_from_dict(content_doc_to_scores)
    content_doc_to_scores = process_query(postings_handler, dictionary, doc_properties, query, is_boolean, is_title=False)
    title_dictionary = load_data(TITLE_DICTIONARY_FILE)
    title_postings = open(TITLE_POSTINGS_FILE, 'rb')
    title_doc_to_scores = process_query(title_postings, title_dictionary, doc_properties, query, is_boolean, is_title=True)

    score_dict = merge_doc_to_score_dicts([content_doc_to_scores, title_doc_to_scores], [CONTENT_WEIGHT, TITLE_WEIGHT])
    top_docs = get_top_scores_from_dict(score_dict)
    return top_docs

def get_top_scores_from_dict(score_dict):
    '''
    Using a min-heap, the documents with the highest scores is retrieved.
    :param score_dict: a dictionary mapping docIDs to scores.
    :return: a list of most relevant documents as docIDs (strings).
    '''
    doc_score_pairs = list(score_dict.items())
    score_list = list(map(lambda x: (-x[1], x[0]), doc_score_pairs))
    top_results = heapq.nsmallest(MAX_DOCS, score_list, key=lambda x: (x[0], x[1]))  # smallest since min_heap is used
    top_documents = list(map(lambda x: str(x[1]), top_results))
    return top_documents

def process_query(postings_handler, dictionary, doc_properties, query, is_boolean, is_title):
    '''
    Each query is represented as a list of either single word terms or phrases stored as lists. The queries are
    processed as follows:
    1. Using the get_term_frequencies function, a list of (term, term frequency) tuples are retrieved.
    2. The (term, term frequency) tuples are separated into lists of single worda, biwords and triwords.
    3. The postings lists for the single words, biwords and triwords are retrieved.
    4. If the query is boolean, the postings lists are intersected i.e. any document that does not contain all the terms
    is removed.
    5. The scores for the single words, biwords and triwords are separately computed using the Eval class, which returns
    a score dictionary mapping documents to their cosine scores. This is done since single words and phrasal terms
    are evaluated as separate query vectors which are linearly weighted.
    6. Finally, the dictionaries are merged into a combined dictionary.
    :param postings_handler: a handler to access the postings list file.
    :param dictionary: the dictionary mapping terms to pointers to each posting list in the postings handler.
    :param doc_properties: the dictionary mapping documents to various properties such as document vector length.
    :param query: a list of terms, which can either be single words or phrases stored as lists.
    :param is_title: true if field to be searched is the title.
    :param is_boolean: true if the query is boolean.
    '''
    query_terms = list(filter(lambda x: type(x) == list or x in dictionary, query)) # remove terms not in dic
    query_terms = get_term_frequencies(query_terms, dictionary)

    single_words = list(filter(lambda x: (type(x[0]) != tuple), query_terms))
    single_words += list(map(lambda x: (x[0][0], x[1]), list(filter(lambda x: (type(x[0]) == tuple and len(x[0]) == 1), query_terms))))
    biwords = list(filter(lambda x: type(x[0]) == tuple and len(x[0]) == 2, query_terms))
    triwords = list(filter(lambda x: type(x[0]) == tuple and len(x[0]) == 3, query_terms))

    single_word_plists = get_posting_lists(postings_handler, single_words, dictionary)
    biword_plists = get_phrase_posting_lists(postings_handler, biwords, dictionary)
    triword_plists = get_phrase_posting_lists(postings_handler, triwords, dictionary)

    if is_boolean:
        single_word_plists, biword_plists, triword_plists = get_intersected_posting_lists(single_word_plists,
                                                                                          biword_plists, triword_plists)

    single_word_scores = Eval(single_words, single_word_plists, dictionary, doc_properties, is_title=is_title).eval_query()
    biword_scores = Eval(biwords, biword_plists, dictionary, doc_properties, term_length=2, is_title=is_title).eval_query()
    triword_scores = Eval(triwords, triword_plists, dictionary, doc_properties, term_length=3, is_title=is_title).eval_query()

    score_dict = merge_doc_to_score_dicts([single_word_scores, biword_scores, triword_scores],
                             [SINGLE_TERMS_WEIGHT, BIWORD_PHRASES_WEIGHT, TRIWORD_PHRASES_WEIGHT])
    return score_dict

def relevance_feedback(postings_handler, dictionary, doc_properties, query, relevant_docs):
    '''
    A function for relevance feedback using the Rocchio algorithm.
    1. The query is converted into a list of (term, term frequency) tuples. This is used to generate the original query
    vector.
    2. A query vector dictionary is constructed which maps terms to the tf-idf of each term.
    3. The relevant documents and the query vector dictionary is passed to the get_new_query_vector function
    which returns a new query vector after relevance expansion in the form of a dictionary mapping terms to their
    tf-idf.
    4. The postings lists for the terms in the new query vector are retrieved.
    5. The cosine scores for each term based on the new query vector are evaluated using Eval, and the top
    documents are returned.
    :param postings_handler: a handler to access the postings list file.
    :param dictionary: the dictionary mapping terms to pointers to each posting list in the postings handler.
    :param doc_properties: the dictionary mapping documents to various properties such as document vector length.
    :param query: a list of terms, which can either be single words or phrases stored as lists.
    :param relevant_docs: a list of documents already identified as relevant.
    :return: a list of relevant documents.
    '''
    relevant_docs = list(map(lambda x: int(x), relevant_docs))
    query = list(filter(lambda x: type(x) != list, query))
    terms = get_term_frequencies(query, dictionary)
    query_vector = Eval(query, [], dictionary, doc_properties).get_query_vector(terms)
    terms = list(map(lambda x: x[0], terms))
    query_vector_dic = dict(zip(terms, query_vector))

    new_query_vector = list(get_new_query_vector(query_vector_dic, relevant_docs).items())
    terms = list(map(lambda x: x[0], new_query_vector))
    tf_idf = list(map(lambda x: x[1], new_query_vector))
    posting_lists = get_posting_lists(postings_handler, terms, dictionary)
    new_query_scores = Eval(terms, posting_lists, dictionary, doc_properties, query_vector=tf_idf).eval_query()
    top_docs = get_top_scores_from_dict(new_query_scores)
    return top_docs