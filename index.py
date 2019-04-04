#!/usr/bin/python
import getopt
import sys
from index_helper import *
from data_helper import *
import time
import multiprocessing
import signal

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda *i, **kwargs: i[0]
# tqdm = lambda *i, **kwargs: i[0] # this is to disable tqdm

########################### DEFINE CONSTANTS ###########################

CSV_FILE_TEST = 'data\\first100.csv'
DICTIONARY_FILE_TEST = 'dictionary.txt'
POSTINGS_FILE_TEST = 'postings.txt'

DOC_ID_NO, TITLE_NO, CONTENT_NO, DATE_POSTED_NO, COURT_NO = range(5)

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

    def normalise_term(t):
        return PORTER_STEMMER.stem(t.lower())

    result = [normalise_term(w) for w in nltk.word_tokenize(row[CONTENT_NO])]

    return row[DOC_ID_NO], result


def main():
    # For lazy mode since we are lazy
    if len(sys.argv) <= 1:
        dataset_file, output_file_dictionary, output_file_postings = CSV_FILE_TEST, DICTIONARY_FILE_TEST, POSTINGS_FILE_TEST
    else:
        dataset_file, output_file_dictionary, output_file_postings = read_files()

    dictionary = Dictionary(output_file_dictionary)
    postings = PostingList(output_file_postings)
    length = dict()

    df = read_csv(dataset_file)

    df = df.sort_values("document_id", ascending=True)
    total_num_documents = df.shape[0]

    # multiprocessing way
    # The proper way to handle CTRL-C
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGINT, original_sigint_handler)

    with multiprocessing.Pool(4) as pool:
        try:
            result = pool.imap(ntlk_tokenise_func, df.itertuples(index=False, name=False))
            for row in tqdm(result, total=total_num_documents):
                id, content = row
                process_doc_direct(id, content, dictionary, postings, length)

            save_data(dictionary, postings, length, total_num_documents)
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
def save_data(dictionary, postings, length, total_num_documents):
    postings.save_to_disk(length, dictionary)
    dictionary.save_to_disk(total_num_documents)


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Time Taken: " + str(end - start))
