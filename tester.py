import pandas as pd
import sys
from data_helper import *
from search_helper import *
from QueryExpansion import *
from constants import *
from pprint import pprint
# filepath = "data\\first100.csv"
# df = pd.read_csv(filepath, date_parser=False)


# df1  = df[df.duplicated(['document_id'])]

# df2 = df.iloc[0:100]

# df3 = pd.concat([df1,df2])

# df3.to_csv("data\\first110.csv", index=False)

# d = get_new_query_offset([2725285])
# from operator import itemgetter
# for k, v in sorted(d.items(), key=itemgetter(1)):
#     print (k, v)

# document_properties[docID][VECTOR_OFFSET])

# for line in open("queries/validation/queries1.txt", encoding='utf-8').readlines():
#     a = get_new_query_strings(line.strip())
#     pprint(a)

# pprint(thesaurize_term("phone call"))
# a = get_new_query_strings('"damages"')
# print(a)

# a = get_new_query_strings('"fertility treatment" AND damages')
# pprint(a)

# a = get_new_query_strings('"fertility treatment" AND "damages you"')
# pprint(a)

# dictionary = load_data(DICTIONARY_FILE_TEST)
# if "phone" in dictionary:
#     print(dictionary["call"])
# dictionary 
# a = get_new_query_strings('quiet AND "phone call"')
# print(a)

# pprint(normalise_term("telephone"))

# def chain_check(lookup, list_of_terms):
#     for term in list_of_terms:
#         term = normalise_term(term)
#         if term in lookup:
#             continue
#         else: 
#             return False
#     return True
            
# line = "pretend to be officer"
# terms = line.split()
# for docID, value in document_properties.items():
#     vector = get_new_query_offset([docID])
#     if chain_check(vector, terms):
#         print(docID)
