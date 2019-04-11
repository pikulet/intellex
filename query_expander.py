from data_helper import load_data, load_data_with_handler
from constants import *
from properties_helper import VECTOR_OFFSET
import math

########################### DEFINE CONSTANTS ###########################

vector_post_file_handler = open(VECTOR_POSTINGS_FILE, 'rb')
document_properties = load_data(DOCUMENT_PROPERTIES_FILE)
total_num_documents = len(document_properties)
log_tf = lambda x: 1 + math.log(x, 10)
idf_transform = lambda x: math.log(total_num_documents/x, 10)

######################## DRIVER FUNCTION ########################


def get_new_query_vector(vector, docIDs):
    """
    Ricco Feedback Public Method.

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


def trimVector(vector):
    """
    Since Ricco will return a large vector, we will implement a min score for each term.
    Those terms that do not meet the point will be removed
    """
    new_vector = dict()
    for key, value in vector.items():
        if value > RICCO_MIN_CUTOFF_POINT:
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
    print(get_new_query_vector({"le": 01.12}, ["246391"]))
    # print(get_vector_from_docID_offset(290883617))
    # for docID, value in document_properties.items():
    #     get_vector_from_docID_offset(value[4])
    # print(get_vector_from_docID_offset(484612308))
    # print(document_properties)
