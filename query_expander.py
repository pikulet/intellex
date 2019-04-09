import random
from index import VECTOR_POSTINGS_FILE
from search_helper import *
from data_helper import *
from properties_helper import DOCUMENT_PROPERTIES_FILE, VECTOR_OFFSET
from pprint import pprint
import multiprocessing
import heapq
import math
try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda *i, **kwargs: i[0]

########################### DEFINE CONSTANTS ###########################

IDF_MODE = True

######################## DRIVER FUNCTION ########################

vector_post_file_handler = open(VECTOR_POSTINGS_FILE, 'rb')
document_properties = get_document_properties(DOCUMENT_PROPERTIES_FILE) # this is actually called in search.py already.

def extractValue(tuple):
    """
    Helper method. Since the vector_post stores tf, idf as a tuple pair
    """
    if IDF_MODE:
        return tuple[0] * tuple[1]
    else:
        return tuple[0]


def get_vector_from_docID_offset(offset):
    """
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
    Given a set of docIDs, get the new offset to be used in the formula aka Centroid
    """
    offset = {}
    for docID in docIDs:
        vector, normalisator = get_vector_from_docID_offset(
            vector_dict[docID][4])
        for key, value in vector.items():
            offset[key] = offset.get(key, 0.) + \
                (extractValue(value) / normalisator)

    # Take average
    for k in offset.keys():
        offset[k] /= len(docIDs)

    return offset


def get_new_query_vector(original_vector, docIDs):
    """
    Given original query vector and list of docIDs

    Calculate Centroid from docIDs and add it to original query vector
    """
    vector = original_vector.copy()
    offset = get_new_query_offset(docIDs)
    for key, value in offset.items():
        vector[key] = vector.get(key, 0.) + value
    return vector


def query_parallel(vector, N):
    """
    VSM Stuff. Run query vector with the other vectors in the model. Return N number of docIDs.
    """
    score_list = []
    with multiprocessing.Pool(4) as pool:
        result = pool.imap_unordered(query_parallel_util, [(
            docID, list[4], vector) for docID, list in vector_dict.items()], chunksize=50)
        for docID, score in tqdm(result, total=len(vector_dict.keys())):
            score_list.append((-score, docID))
    top_results = heapq.nsmallest(N, score_list, key=lambda x: (
        x[0], x[1]))  # smallest since min_heap is used
    top_documents = list(map(lambda x: str(x[1]), top_results))

    return top_results


def query_parallel_util(pair):
    """
    Util Method. Ignore.
    """
    docID, offset, vector = pair
    score = 0.
    docVector, normalisator = get_vector_from_docID_offset(offset)
    for key, value in vector.items():
        if key in docVector:
            score += extractValue(docVector[key]) / normalisator * value
    return docID, score

# def query(vector, N):
#     vector_dict = load_data("dictionaryvector.txt")

#     score_list = []
#     for docID in tqdm(vector_dict.keys(), total = len(vector_dict.keys())):
#         score = 0.
#         docVector = get_vector_from_docID(docID)
#         for key, value in vector.items():
#             if key in docVector:
#                 score += extractValue(docVector[key]) * value
#         score_list.append((-score, docID))

#     top_results = heapq.nsmallest(N, score_list, key=lambda x: (x[0], x[1]))  # smallest since min_heap is used
#     top_documents = list(map(lambda x: str(x[1]), top_results))

#     return top_documents


###
# Ignore. Just a test main()
###
def coin_toss(value):
    return value if random.random() < 0.5 else 0


if __name__ == '__main__':
    def get_vector_from_docID(docID):
        # vector are stored as sparse indexes
        # each valid index will map to (tf, idf)
        offset = document_properties[docID][VECTOR_OFFSET]
        data = load_data_with_handler(vector_post_file_handler, offset)
        return data

    import time
    start = time.time()
    old_query = {key: coin_toss(
        value[0]) for key, value in get_vector_from_docID(246788).items()}
    new_query = get_new_query_vector(old_query, [246788, 246781])
    pprint(query_parallel(new_query, 15))
    end = time.time()
    print(end-start)

    # print(set(get_vector([246788, 246781])) & set(get_vector2([246788, 246781])))
