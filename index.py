#!/usr/bin/python
import getopt
import sys
from index_helper import *
import pandas as pd

########################### DEFINE CONSTANTS ###########################
LAZY_MODE = True
CSV_FILE_TEST = 'data\\first100.csv'
DICTIONARY_FILE_TEST = 'dictionary.txt'
POSTINGS_FILE_TEST = 'postings.txt'

######################## COMMAND LINE ARGUMENTS ########################

### Read in the input files as command-line arguments
###
def read_files():
    def usage():
        print("usage: " + sys.argv[0] + " -i dataset-file -d dictionary-file -p postings-file")

    dataset_file = output_file_dictionary = output_file_postings = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-i': # input directory
            dataset_file = a
        elif o == '-d': # dictionary file
            output_file_dictionary = a
        elif o == '-p': # postings file
            output_file_postings = a
        else:
            assert False, "unhandled option"

    if dataset_file == None or output_file_postings == None or output_file_dictionary == None:
        usage()
        sys.exit(2)

    return dataset_file, output_file_dictionary, output_file_postings

######################## DRIVER FUNCTION ########################

def main():
    if LAZY_MODE:
        dataset_file, output_file_dictionary, output_file_postings = CSV_FILE_TEST, DICTIONARY_FILE_TEST, POSTINGS_FILE_TEST
    else:
        dataset_file, output_file_dictionary, output_file_postings = read_files()

    dictionary = Dictionary(output_file_dictionary)
    postings = PostingList(output_file_postings)
    length = dict()
    
    df = pd.read_csv(dataset_file)
    NO, DOC_ID, TITLE, CONTENT, DATE_POSTED, COURT = list(df)

    df = df.sort_values("document_id", ascending=True)
    total_num_documents = 0
    
    for index, row in df.iterrows():
        process_doc(row[DOC_ID], row[CONTENT], dictionary, postings, length)
        total_num_documents += 1

    save_data(dictionary, postings, length, total_num_documents)

### Save the indexing data to disk
###
def save_data(dictionary, postings, length, total_num_documents):
    postings.save_to_disk(length, dictionary)
    dictionary.save_to_disk(total_num_documents)

if __name__ == "__main__":
    main()
    
