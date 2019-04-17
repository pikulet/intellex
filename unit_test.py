from constants import *
from data_helper import *
from search_helper import *
from QueryExpansion import *
import pandas as pd
import sys
from pprint import pprint

### Unit Test File.
###

### Rocchio Test Case
def run_test_rocchio():
    print(get_new_query_vector({"le": 01.12}, ["246391"]))
    for docID, value in document_properties.items():
        get_vector_from_docID_offset(value[4])

### WordNet Test Case
def run_test_wordnet():
    test_strs = ['quiet "phone call"', '"phone call" quiet', 'quiet AND "phone call"' ]

    for test_str in test_strs:
        bool1, bool2, result = tokenize(test_str)
        print (result)
        for term in result:
            print(thesaurize_term(term))
        print("\n")

### Query Expander Test case
def run_test_query_expand():
    for line in open("queries/validation/queries1.txt", encoding='utf-8').readlines():
        a = get_new_query_strings(line.strip())
        print(a)

if __name__ == "__main__":
    run_test_rocchio()
    run_test_wordnet()
    run_test_query_expand()