######################## 
# Global Constants File
# 
# All Constants that can be modified should be placed here
######################## 

DF_DOC_ID_NO, DF_TITLE_NO, DF_CONTENT_NO, DF_DATE_POSTED_NO, DF_COURT_NO = range(5)
TEMBUSU_MODE = False
PROCESS_COUNT = 6 if TEMBUSU_MODE else 3
BATCH_SIZE = 5 if TEMBUSU_MODE else 5

CSV_FILE_TEST = "data\\first100.csv"
#CSV_FILE_TEST = "data\\dataset.csv"
DICTIONARY_FILE_TEST = "dictionary.txt"
POSTINGS_FILE_TEST = "postings.txt"
QUERY_FILE_TEST = 'queries\\q1.txt'
OUTPUT_FILE_TEST = 'output.txt'

## Extra files
TITLE_DICTIONARY_FILE = "dictionarytitle.txt"
TITLE_POSTINGS_FILE = "postingstitle.txt"
VECTOR_DICTIONARY_FILE = "dictionaryvector.txt"
VECTOR_POSTINGS_FILE = "postingsvector.txt"
DOCUMENT_PROPERTIES_FILE = "properties.txt"

## Cut off points
RICCO_MIN_CUTOFF_POINT = 0.05

## Weights
SINGLE_TERMS_WEIGHT = 1
BIWORD_PHRASES_WEIGHT = 1
TRIWORD_PHRASES_WEIGHT = 1
TITLE_WEIGHT = 1
CONTENT_WEIGHT = 1
