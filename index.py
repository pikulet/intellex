#!/usr/bin/python
import getopt
import sys
from index_helper import *
from data_helper import *
from properties_helper import *
import time
import multiprocessing
import signal
import math

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda *i, **kwargs: i[0]
# tqdm = lambda *i, **kwargs: i[0] # this is to disable tqdm

########################### DEFINE CONSTANTS ###########################

CSV_FILE_TEST = 'data\\first100.csv'
DICTIONARY_FILE_TEST = 'dictionary.txt'
POSTINGS_FILE_TEST = 'postings.txt'

DF_DOC_ID_NO, DF_TITLE_NO, DF_CONTENT_NO, DF_DATE_POSTED_NO, DF_COURT_NO = range(5)
TEMBUSU_MODE = True if multiprocessing.cpu_count() > 10 else False
PROCESS_COUNT = 4 if TEMBUSU_MODE else 4
BATCH_SIZE = 5 if TEMBUSU_MODE else 5

## Extra files
TITLE_DICTIONARY_FILE = "dictionarytitle.txt"
TITLE_POSTINGS_FILE = "postingstitle.txt"
VECTOR_DICTIONARY_FILE = "dictionaryvector.txt"
VECTOR_POSTINGS_FILE = "postingsvector.txt"

######################## COMMAND LINE ARGUMENTS ########################

# Read in the input files as command-line arguments
###


def read_files():
    def usage():
        print(
            "usage: " + sys.argv[0] + " -i dataset-file -d dictionary-file -p postings-file")

    dataset_file = output_file_dictionary = output_file_postings = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-i':  # input directory
            dataset_file = a
        elif o == '-d':  # dictionary file
            output_file_dictionary = a
        elif o == '-p':  # postings file
            output_file_postings = a
        else:
            assert False, "unhandled option"

    if dataset_file == None or output_file_postings == None or output_file_dictionary == None:
        usage()
        sys.exit(2)

    return dataset_file, output_file_dictionary, output_file_postings

######################## DRIVER FUNCTION ########################

def ntlk_tokenise_func(row):
    import nltk
    from nltk.stem.porter import PorterStemmer
    PORTER_STEMMER = PorterStemmer()

    content = [normalise_term(w) for w in nltk.word_tokenize(row[DF_CONTENT_NO])]
    title = [normalise_term(w) for w in nltk.word_tokenize(row[DF_TITLE_NO])]
    date = row[DF_DATE_POSTED_NO]
    court = str(row[DF_COURT_NO])

    return row[DF_DOC_ID_NO], title, content, date, court

def main():
    # For lazy mode since we are lazy
    if len(sys.argv) <= 1:
        dataset_file, output_file_dictionary, output_file_postings = CSV_FILE_TEST, DICTIONARY_FILE_TEST, POSTINGS_FILE_TEST
    else:
        dataset_file, output_file_dictionary, output_file_postings = read_files()

    dictionary = Dictionary(output_file_dictionary)
    postings = PostingList(output_file_postings)

    dictionary_title = Dictionary(TITLE_DICTIONARY_FILE)
    postings_title = PostingList(TITLE_POSTINGS_FILE)

    df = read_csv(dataset_file)
    df = df.sort_values("document_id", ascending=True)
    total_num_documents = df.shape[0]
    
    print("Running indexing...")

    # multiprocessing way
    # The proper way to handle CTRL-C
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGINT, original_sigint_handler)

    document_vectors = dict()
    bigram_index = dict()
    trigram_index = dict()
    bitriword_frequency = dict()
    with multiprocessing.Pool(PROCESS_COUNT) as pool:
        try:
            result = pool.imap(ntlk_tokenise_func, df.itertuples(index=False, name=False), chunksize=BATCH_SIZE)
            for row in tqdm(result, total=total_num_documents):
                docID, title, content, date, court = row

                create_empty_property_list(docID)                
                content_vector, content_length = process_doc_direct(docID, content, dictionary, postings, bigram_index, trigram_index, bitriword_frequency)
                title_vector, title_length = process_doc_direct(docID, title, dictionary_title, postings_title)
                
                document_vectors[docID] = content_vector
                assign_property(docID, CONTENT_LENGTH, content_length)
                assign_property(docID, TITLE_LENGTH, title_length)
                assign_property(docID, COURT_PRIORITY, get_court_priority(court))
                assign_property(docID, DATE_POSTED, get_recent_level(date))

            print("Saving...")

            save_vector(dictionary, total_num_documents, document_vectors)
            save_data(dictionary, postings, total_num_documents)
            save_data(dictionary_title, postings_title, total_num_documents)
            save_gram_data(BIGRAM_FACTOR, bigram_index, bitriword_frequency, total_num_documents)
            save_gram_data(TRIGRAM_FACTOR, trigram_index, bitriword_frequency, total_num_documents)
            store_data(DOCUMENT_PROPERTIES_FILE, document_properties)



        except (KeyboardInterrupt):
            print("Caught KeyboardInterrupt. Terminating workers!")
            pool.terminate()


    # non-multiprocessing way
    # DOC_ID, TITLE, CONTENT, DATE_POSTED, COURT = list(df)

    # for index, row in tqdm(df.iterrows(), total=total_num_documents):
    #     process_doc(row[DOC_ID], row[CONTENT], dictionary, postings, length)
    # save_data(dictionary, postings, length, total_num_documents)

# Save the indexing data to disk
###
def save_data(dictionary, postings, total_num_documents):
    postings.save_to_disk(dictionary)
    dictionary.save_to_disk(total_num_documents)

# Save the vector data to disk
###
def save_vector(dictionary, total_num_documents, document_vectors):

    idf_transform = lambda x: math.log(total_num_documents/x, 10)

    pfile = VECTOR_POSTINGS_FILE
    pfilehandler = open(pfile, 'wb')

    for docID, vector in tqdm(document_vectors.items(), total=total_num_documents):
        for t in vector:
            vector[t] = (vector[t], idf_transform(dictionary.terms[t][Dictionary.DF]))
        
        assign_property(docID, VECTOR_OFFSET, pfilehandler.tell())
        store_data_with_handler(pfilehandler, vector)      

# Save the gram data to disk
###
def save_gram_data(DOCUMENT_TYPE, gram_index, bitriword_frequency, total_num_documents):
    log_tf = lambda x: 1 + math.log(x, 10)
    idf_transform = lambda x: math.log(total_num_documents/x, 10)

    docID_gram_normalisator = dict()
    for docID, gram_index_t in gram_index.items():
        normalisator = 0.
        for term, count in gram_index_t.items():
            normalisator += (log_tf(count) * idf_transform(bitriword_frequency[term]) ) ** 2

        normalisator = math.sqrt(normalisator)
        assign_property(docID, DOCUMENT_TYPE, normalisator)

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Time Taken: " + str(end - start))
