from search_helper import *
from data_helper import *
from pprint import pprint
import heapq
try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda *i, **kwargs: i[0]

########################### DEFINE CONSTANTS ###########################

IDF_MODE = False

######################## DRIVER FUNCTION ########################


vector_dict = load_data("dictionaryvector.txt")
vector_value = open("postingsvector.txt", 'rb')
idf_transform = lambda x: math.log(total_num_documents/x, 10)

def extractValue(tuple):
    if IDF_MODE:
        return tuple[0] * idf_transform(tuple[1])
    else:
        return tuple[0]

'''
Given the docID, get the vector dict
'''

def get_vector_from_docID(docID):
    # vector are stored as sparse indexes
    # each valid index will map to (tf, idf)
    offset = vector_dict[docID]
    data = load_data_with_handler(vector_value, offset)
    return data

def get_vector_from_offset(offset):
    # vector are stored as sparse indexes
    # each valid index will map to (tf, idf)
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
    offset = get_new_vector_offset(docIDs)
    for key, value in offset.items():
        vector[key] = vector.get(key, 0.) + value

    return vector

def query_parallel_util(pair):
    docID, offset, vector = pair
    score = 0.
    docVector = get_vector_from_offset(offset)
    for key, value in vector.items():  
            if key in docVector:
                score += extractValue(docVector[key]) * value
    return docID, score

import multiprocessing

def query_parallel(vector, N):
    vector_dict = load_data("dictionaryvector.txt")

    score_list = []
    with multiprocessing.Pool(4) as pool:
        result = pool.imap_unordered(query_parallel_util, [(docID, offset, vector) for docID, offset in vector_dict.items()], chunksize=50)
        for docID, score in tqdm(result, total=len(vector_dict.keys())):
            score_list.append((-score, docID))
    top_results = heapq.nsmallest(N, score_list, key=lambda x: (x[0], x[1]))  # smallest since min_heap is used
    top_documents = list(map(lambda x: str(x[1]), top_results))
    
    return top_documents

def query(vector, N):
    score_list = []
    for docID in tqdm(vector_dict.keys(), total = len(vector_dict.keys())):
        score = 0.
        docVector = get_vector_from_docID(docID)
        for key, value in vector.items():  
            if key in docVector:
                score += extractValue(docVector[key]) * value
        score_list.append((-score, docID))
    
    top_results = heapq.nsmallest(N, score_list, key=lambda x: (x[0], x[1]))  # smallest since min_heap is used
    top_documents = list(map(lambda x: str(x[1]), top_results))
    
    return top_results

import random 

def coin_toss(value):
    return value if random.random() < 0.5 else 0

if __name__ == '__main__':
    vector_dict = load_data("dictionaryvector.txt")
    import time
    start = time.time()
    # get_vector(246788)
    old_query = {key: coin_toss(value[0]) for key,value in get_vector_from_docID(246788).items()}
    new_query = get_new_query_vector(old_query, [246788, 246781])
    pprint(query_parallel(new_query, 10))
    end = time.time()
    print (end-start)

    # print(set(get_vector([246788, 246781])) & set(get_vector2([246788, 246781])))
