#!/usr/bin/python
from index_helper import *
from data_helper import *
from properties_helper import *
from constants import *
import time
import multiprocessing
import signal
import math
from nltk import word_tokenize
import getopt
import sys

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda *i, **kwargs: i[0]
# tqdm = lambda *i, **kwargs: i[0] # this is to disable tqdm

########################### DEFINE CONSTANTS ###########################

PORTER_STEMMER = PorterStemmer()

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

### Data parallelization method to speed up nltk word_tokenize
def ntlk_tokenise_func(row):
    content = [normalise_term(w) for w in word_tokenize(row[DF_CONTENT_NO])]
    title = [normalise_term(w) for w in word_tokenize(row[DF_TITLE_NO])]
    date = row[DF_DATE_POSTED_NO]
    court = str(row[DF_COURT_NO])

    return row[DF_DOC_ID_NO], title, content, date, court

## util function
def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


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

    total_num_documents = df.shape[0]
    
    print("Running indexing...")

    # Storage dictionaries
    uniword_vectors = dict()
    
    # multiprocessing way
    # The proper way to handle CTRL-C
    with multiprocessing.Pool(PROCESS_COUNT, init_worker) as pool:
        try:
            result = pool.imap(ntlk_tokenise_func, df.itertuples(index=False, name=False), chunksize=BATCH_SIZE)
            for row in tqdm(result, total=total_num_documents):
                docID, title, content, date, court = row

                if docID in document_properties:
                    # only the highest court priority is saved
                    update_court(docID, get_court_priority(court))
                    continue
                    
                create_empty_property_list(docID)                
                content_uniword_vector, content_biword_vector, content_triword_vector = process_doc_vector_and_bigram_trigram(docID, content, dictionary, postings)
                title_uniword_vector, title_biword_vector, title_triword_vector = process_doc_vector_and_bigram_trigram(docID, title, dictionary_title, postings_title)
                
                content_uniword_length = get_length(content_uniword_vector)
                content_biword_length = get_length(content_biword_vector)
                content_triword_length = get_length(content_triword_vector)

                title_uniword_length = get_length(title_uniword_vector)
                title_biword_length = get_length(title_biword_vector)
                title_triword_length = get_length(title_triword_vector)

                uniword_vectors[docID] = content_uniword_vector
                # biword_vectors[docID] = content_biword_vector
                # triword_vectors[docID] = content_triword_vector
                
                assign_property(docID, TITLE_LENGTH, title_uniword_length)
                assign_property(docID, BIGRAM_TITLE_LENGTH, title_biword_length)
                assign_property(docID, TRIGRAM_TITLE_LENGTH, title_triword_length)
                assign_property(docID, COURT_PRIORITY, get_court_priority(court))
                assign_property(docID, CONTENT_LENGTH, content_uniword_length)
                assign_property(docID, BIGRAM_CONTENT_LENGTH, content_biword_length)
                assign_property(docID, TRIGRAM_CONTENT_LENGTH, content_triword_length)

            print("Saving... There are 3 progress bars.")

            save_vector(dictionary, total_num_documents, uniword_vectors)
            save_data(dictionary, postings, total_num_documents)
            save_data(dictionary_title, postings_title, total_num_documents)
            store_data(DOCUMENT_PROPERTIES_FILE, document_properties)


        except (KeyboardInterrupt):
            print("Caught KeyboardInterrupt. Terminating workers!")
            pool.terminate()
        else:
            print("Normal termination")
            pool.close()

### Save the indexing data to disk
def save_data(dictionary, postings, total_num_documents):
    postings.save_to_disk(dictionary)
    dictionary.save_to_disk(total_num_documents)

### Save the vector data to disk
def save_vector(dictionary, total_num_documents, document_vectors):

    idf_transform = lambda x: math.log(total_num_documents/x, 10)

    pfilehandler = open(VECTOR_POSTINGS_FILE, 'wb')

    for docID, vector in tqdm(document_vectors.items(), total=total_num_documents):
        for t in vector:
            # vector[t] = (vector[t], idf_transform(dictionary.terms[t][Dictionary.DF]))
            vector[t] = vector[t] * idf_transform(dictionary.terms[t][Dictionary.DF])

       
        assign_property(docID, VECTOR_OFFSET, pfilehandler.tell())
        store_data_with_handler(pfilehandler, vector)

    pfilehandler.close()

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Time Taken: " + str(end - start))

