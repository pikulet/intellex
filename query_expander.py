from index import normalise_term, DICTIONARY_FILE_TEST, POSTINGS_FILE_TEST
from search_helper import *
import pickle
from index import Dictionary, PostingList
from Eval import Eval
from PositionalMerge import *
from data_helper import *
import pprint

topk = 5
n = 20

'''
Given the docID, get the vector
'''
# dictionary = load_data("dictionary.txt")
# postings = open("postings.txt", 'rb')
# length_dict = load_data_with_handler(postings, 0)
vector_dict = load_data("dictionaryvector.txt")
vector_value = open("postingvector.txt", 'rb')

def get_vector(docID):
    offset = vector_dict[docID]
    data = load_data_with_handler(vector_value, offset)
    return data

# def get_vector2(docID):
#     vector = []
#     for term in dictionary:
#         idf, post = get_posting(postings, dictionary, term)
        
#         for i in post:
#             if i[0] == docID:
#                 tf = i[1]
#                 vector.append(tf * idf)
#                 continue
#         vector.append(0)

#     return vector

def get_new_vector_offset(docIDs):
    offset = []
    for docID in docIDs:
        vector = get_vector(docID)
        if len(offset) == 0:
            offset = vector
        else:
            for i in range(len(offset)):
                offset[i] += vector[i]
    offset = [i / len(docIDs) for i in offset]

    return offset

def get_new_query_vector(original_vector, docIDs):
    vector = original_vector
    docs = docIDs[:topk]
    offset = get_new_vector_offset(docs)
    for i in range(len(vector)):
        vector[i] += offset[i]
    return vector

# get_vector(246788)
# get_new_vector_offset([246788, 246781])

# print(set(get_vector([246788, 246781])) & set(get_vector2([246788, 246781])))

