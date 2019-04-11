######################## 
# Constants File
#
######################## 

DF_DOC_ID_NO, DF_TITLE_NO, DF_CONTENT_NO, DF_DATE_POSTED_NO, DF_COURT_NO = range(5)
TEMBUSU_MODE = False
PROCESS_COUNT = 6 if TEMBUSU_MODE else 3
BATCH_SIZE = 5 if TEMBUSU_MODE else 5

CSV_FILE_TEST = "data\\first100.csv"
DICTIONARY_FILE_TEST = "../dictionary.txt"
POSTINGS_FILE_TEST = "../postings.txt"

## Extra files
TITLE_DICTIONARY_FILE = "../dictionarytitle.txt"
TITLE_POSTINGS_FILE = "../postingstitle.txt"
VECTOR_DICTIONARY_FILE = "../dictionaryvector.txt"
VECTOR_POSTINGS_FILE = "../postingsvector.txt"
DOCUMENT_PROPERTIES_FILE = "../properties.txt"

##
RICCO_MIN_CUTOFF_POINT = 0.01