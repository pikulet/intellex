from search_helper import *
from data_helper import *
from pprint import pprint

########################### DEFINE CONSTANTS ###########################

TOPK = 5
N = 100

######################## DRIVER FUNCTION ########################

'''
Given the docID, get the vector dict
'''

vector_dict = load_data("dictionaryvector.txt")
vector_value = open("postingvector.txt", 'rb')


def get_vector_from_docID(docID):
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
            offset[key] = offset.get(key, 0.) + value

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

def query(vector):
    scores = {}
    for docID in vector_dict.keys():
        score = 0.
        for key, value in vector.items():  
            docVector = get_vector_from_docID(docID)
            if key in docVector:
                score += docVector[key] * value
        scores[docID] = score

# get_vector(246788)
new_query = get_new_query_vector(get_vector_from_docID(246788), [246788, 246781])
pprint(query(new_query))

# print(set(get_vector([246788, 246781])) & set(get_vector2([246788, 246781])))
