from search_helper import *
from data_helper import *
from pprint import pprint
import multiprocessing
import heapq
import math
try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda *i, **kwargs: i[0]

########################### DEFINE CONSTANTS ###########################

IDF_MODE = False

######################## DRIVER FUNCTION ########################

vector_value = open("postingsvector.txt", 'rb')
vector_dict = load_data("properties.txt")
idf_transform = lambda x: math.log(total_num_documents/x, 10)

def extractValue(tuple):
    if IDF_MODE:
        return tuple[0] * idf_transform(tuple[1])
    else:
        return tuple[0]

'''
Given the docID offset, get the vector dict
'''

def get_vector_from_docID_offset(offset):
    # vector are stored as sparse indexes
    # each valid index will map to (tf, idf)
    data = load_data_with_handler(vector_value, offset)

    # we need to normalise
    normalisator = 0.
    for key, value in data.items():
        normalisator += extractValue(value) ** 2
    normalisator = math.sqrt(normalisator)

    return data, normalisator


'''
Given a set of docIDs, get the new offset to be used in the formula aka Centroid
'''

def get_new_query_offset(docIDs):
    offset = {}
    for docID in docIDs:
        vector, normalisator = get_vector_from_docID_offset(vector_dict[docID][4])
        for key, value in vector.items():
            offset[key] = offset.get(key, 0.) + (extractValue(value) / normalisator)

    # Take average
    for k in offset.keys():
        offset[k] /= len(docIDs)

    return offset

'''
Add Centroid to original vector
'''

def get_new_query_vector(original_vector, docIDs):
    vector = original_vector.copy()
    offset = get_new_query_offset(docIDs)
    for key, value in offset.items():
        vector[key] = vector.get(key, 0.) + value
    return vector



'''
VSM Stuff. Run query vector with the other vectors in the model. Run N number of docIDs
'''

def query_parallel(vector, N):
    score_list = []
    with multiprocessing.Pool(4) as pool:
        result = pool.imap_unordered(query_parallel_util, [(docID, list[4], vector) for docID, list in vector_dict.items()], chunksize=50)
        for docID, score in tqdm(result, total=len(vector_dict.keys())):
            score_list.append((-score, docID))
    top_results = heapq.nsmallest(N, score_list, key=lambda x: (x[0], x[1]))  # smallest since min_heap is used
    top_documents = list(map(lambda x: str(x[1]), top_results))
    
    return top_results

'''
Util Method. Ignore.
'''

def query_parallel_util(pair):
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

'''
Ignore. Just a test main()
'''
import random 
def coin_toss(value):
    return value if random.random() < 0.5 else 0

if __name__ == '__main__':
    def get_vector_from_docID(docID):
        # vector are stored as sparse indexes
        # each valid index will map to (tf, idf)
        offset = vector_dict[docID][4]
        data = load_data_with_handler(vector_value, offset)
        return data

    import time
    start = time.time()
    old_query = {key: coin_toss(value[0]) for key,value in get_vector_from_docID(246788).items()}
    new_query = get_new_query_vector(old_query, [246788, 246781])
    pprint(query_parallel(new_query, 15))
    end = time.time()
    print (end-start)

    # print(set(get_vector([246788, 246781])) & set(get_vector2([246788, 246781])))
