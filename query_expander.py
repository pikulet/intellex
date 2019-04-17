from data_helper import *
from constants import *
from properties_helper import VECTOR_OFFSET
import math
import re
from nltk.corpus import wordnet as wn

########################### DEFINE CONSTANTS ###########################

vector_post_file_handler = open(VECTOR_POSTINGS_FILE, 'rb')
document_properties = load_data(DOCUMENT_PROPERTIES_FILE)
total_num_documents = len(document_properties)


def log_tf(x): return 1 + math.log(x, 10)


def idf_transform(x): return math.log(total_num_documents/x, 10)

######################## DRIVER FUNCTION ########################


def get_new_query_strings(line):
    """
    Query Expansion Public Method

    Given the original query string,

    return a list of new query strings generated using predefined rules
    """
    result = []

    is_bool, is_phrase, tokens = tokenize(line)

    newlinelist = tokens
    result.append(convert_list_to_string(newlinelist))  # original query

    # everything after here does not require order, but must be distinct
    tokens = set(tokens)

    if is_phrase and is_bool:
        newlinelist = []
        for token in tokens:
            if token != "AND":
                for subtoken in token.split():
                    newlinelist.append(subtoken)
        result.append(convert_list_to_string(newlinelist))  # no phrase no bool

    if is_bool:
        newlinelist = []
        for token in tokens:
            if token != "AND":
                newlinelist.append(token)
        result.append(convert_list_to_string(newlinelist))  # phrase no bool

    newlinelist = []
    for token in tokens:
        if token != "AND":
            newlinelist += thesaurize_term(token)
    result.append(convert_list_to_string(set(newlinelist)))  # wordnet no bool

    return result


def get_new_query_vector(vector, docIDs):
    """
    Relevance Feedback Public Method

    Given original query vector and list of docIDs.

    The query vector is modelled as sparse vector where it is a term -> score mapping. 
    Zero score terms will not be stored.

    Calculate Centroid from docIDs and add it to original query vector. 

    Trim the vector according to be predefined minium score
    """

    # Guard methods
    if not isinstance(vector, dict):
        raise Exception("Wrong usage of method: vector should be a dict")

    if not isinstance(docIDs, list):
        raise Exception("Wrong usage of method: docIDs should be a list")

    offset = get_new_query_offset(docIDs)
    for key, value in offset.items():
        vector[key] = vector.get(key, 0.) + value

    vector = trimVector(vector)
    return vector

######################## UTIL FUNCTION ########################


def convert_list_to_string(line_list):
    """
    Util function
    convert a list of tokens into string
    add 
    """
    result = ""

    # normalise all tokens first
    line_list = list(line_list)
    for i in range(len(line_list)):
        if i == "AND":
            continue
        line_list[i] = " ".join([normalise_term(x)
                                 for x in line_list[i].split()])

    for line in line_list:
        if line == "AND":
            result += line + " "
            continue
        subline = line.split()
        if len(subline) > 1:
            result += ' "'
            for s in subline:
                result += s + " "
            result = result[:-1]
            result += '" '
        else:
            result += line + ' '
    return result.strip().replace("  ", " ")


def tokenize(line):
    """
    The line will be tokenised to a list of words, using the delimiter as space or "

    For example:

    quiet "phone call"
    ->
    quiet
    phone call

    Also returns is_bool and is_phrase
    """
    is_bool = False
    is_phrase = False
    regex = re.compile('(\w*)|(\"\w* \w*\")')
    result = []
    for group in regex.findall(line):
        for term in group:
            if term:
                if term == "AND":
                    is_bool = True
                if '"' in term:
                    is_phrase = True
                term = term.strip('"')
                result.append(term)
    return is_bool, is_phrase, result


def thesaurize_term(t):
    """
    Given a term t, return an list of unique synonyms.

    If a term that has two words is given, the space will be replaced by a _
    This is the WordNet format
    """
    t = t.replace(" ", "_")
    terms = []
    for synset in wn.synsets(t):
        for item in synset.lemma_names():
            terms.append(item)

    return set(convert_wordnet_terms(terms))


def convert_wordnet_terms(terms):
    """
    Remove some of the unuseable terms such as _
    """
    newterms = []
    for term in terms:
        term = term.replace("_", " ")
        newterms.append(term)
    return newterms


def trimVector(vector):
    """
    Since Ricco will return a large vector, we will implement a min score for each term.
    Those terms that do not meet the point will be removed
    """
    new_vector = dict()
    for key, value in vector.items():
        if value > ROCCHIO_MIN_CUTOFF_POINT:
            new_vector[key] = value
    return new_vector


def extractValue(tuple):
    """
    Undated method. Will be removed soon.
    """
    return log_tf(tuple[0]) *\
        idf_transform(tuple[1])


def get_vector_from_docID_offset(offset):
    """
    Util Method
    Given the docID offset, get the vector dict
    """

    # vector are stored as sparse indexes
    # each valid index will map to (tf, idf)
    data = load_data_with_handler(vector_post_file_handler, offset)

    # we need to normalise
    normalisator = 0.
    for key, value in data.items():
        normalisator += extractValue(value) ** 2
    normalisator = math.sqrt(normalisator)

    return data, normalisator


def get_new_query_offset(docIDs):
    """
    Util Method
    Given a set of docIDs, get the new offset to be used in the formula aka Centroid
    """
    num_of_docs = len(docIDs)
    offset = {}
    for docID in docIDs:
        docID = int(docID)
        vector, normalisator = get_vector_from_docID_offset(
            document_properties[docID][VECTOR_OFFSET])
        for key, value in vector.items():
            normalised = extractValue(value) / normalisator
            offset[key] = offset.get(key, 0.) + normalised

    # Take average
    for k in offset.keys():
        offset[k] /= num_of_docs

    return offset


# TEST METHODS
if __name__ == "__main__":

    # Ricco Test Case
    # print(get_new_query_vector({"le": 01.12}, ["246391"]))
    # print(get_vector_from_docID_offset(290883617))
    # for docID, value in document_properties.items():
    #     get_vector_from_docID_offset(value[4])
    # print(get_vector_from_docID_offset(484612308))
    # print(document_properties)

    # WordNet Test Case
    test_str = 'quiet "phone call"'
    results = []
    result = tokenize(test_str)
    for term in result:
        print(term)
        print(thesaurize_term(term))
