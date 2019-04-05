from search_helper import *
from data_helper import *
from pprint import pprint
import heapq

########################### DEFINE CONSTANTS ###########################

TOPK = 5

######################## DRIVER FUNCTION ########################


vector_dict = load_data("dictionaryvector.txt")
vector_value = open("postingsvector.txt", 'rb')

def extractValue(tuple):
    return tuple[0] * tuple[1]

'''
Given the docID, get the vector dict
'''

def get_vector_from_docID(docID):
    # vector are stored as sparse indexes
    # each valid index will map to (tf, idf)
    offset = vector_dict[docID]
    data = load_data_with_handler(vector_value, offset)
    return data


'''
Given a set of docIDs, get the new offset to be used in the formula
'''


def get_new_vector_offset(docIDs):
    # originalTerms = get_dictionary("dictionary.txt").terms
    offset = {}
    for docID in docIDs:
        vector = get_vector_from_docID(docID)
        for key, value in vector.items():
            offset[key] = offset.get(key, 0.) + extractValue(value)

    # Take average
    for k in offset.keys():
        offset[k] /= len(docIDs)

    return offset


def get_new_query_vector(original_vector, docIDs):
    vector = original_vector.copy()
    docs = docIDs[:TOPK]
    offset = get_new_vector_offset(docs)
    for key, value in offset.items():
        vector[key] = vector.get(key, 0.) + value

    return vector

def query(vector, N):
    score_list = []
    for docID in vector_dict.keys():
        score = 0.
        for key, value in vector.items():  
            docVector = get_vector_from_docID(docID)
            if key in docVector:
                score += extractValue(docVector[key]) * value
        score_list.append((-score, docID))
    
    top_results = heapq.nsmallest(N, score_list, key=lambda x: (x[0], x[1]))  # smallest since min_heap is used
    top_documents = list(map(lambda x: str(x[1]), top_results))
    
    return top_results

# get_vector(246788)
old_query = {key: value[0] for key,value in get_vector_from_docID(246788).items()}
new_query = get_new_query_vector(old_query, [246788, 246781])
pprint(query(new_query, 10))

# print(set(get_vector([246788, 246781])) & set(get_vector2([246788, 246781])))
