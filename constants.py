######################## 
# Global Constants File
# 
# All Constants that can be modified should be placed here
######################## 

DF_DOC_ID_NO, DF_TITLE_NO, DF_CONTENT_NO, DF_DATE_POSTED_NO, DF_COURT_NO = range(5)
TEMBUSU_MODE = False
PROCESS_COUNT = 6 if TEMBUSU_MODE else 3
BATCH_SIZE = 6 if TEMBUSU_MODE else 6

CSV_FILE_TEST = "data\\first100.csv"
#CSV_FILE_TEST = "data\\dataset.csv"
DICTIONARY_FILE_TEST = "dictionary.txt"
POSTINGS_FILE_TEST = "postings.txt"
QUERY_FILE_TEST = 'queries\\q1.txt'
OUTPUT_FILE_TEST = 'output.txt'

## Extra files
TITLE_DICTIONARY_FILE = "dictionary_title.txt"
TITLE_POSTINGS_FILE = "postings_title.txt"
VECTOR_POSTINGS_FILE = "postings_vector.txt"
DOCUMENT_PROPERTIES_FILE = "properties.txt"

## Cut off points
ROCCHIO_MIN_CUTOFF_POINT = 0.01

## Weights
SINGLE_TERMS_WEIGHT = 1
BIWORD_PHRASES_WEIGHT = 1
TRIWORD_PHRASES_WEIGHT = 1
TITLE_WEIGHT = 1
CONTENT_WEIGHT = 1

## Search modes
EXPAND_QUERY = True
NUM_QUERIES_IN_FILE = 1
MULTIPLE_QUERIES_IN_FILE = False
CONTENT_ONLY = True
NUM_DOCS_TO_FEEDBACK = 1000