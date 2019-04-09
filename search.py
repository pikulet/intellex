from index import normalise_term, DICTIONARY_FILE_TEST, POSTINGS_FILE_TEST, DOCUMENT_PROPERTIES_FILE
from search_helper import *
import getopt
import sys

########################### DEFINE CONSTANTS ###########################

END_LINE_MARKER = '\n'
QUERY_FILE_TEST = 'queries\\q1.txt'
OUTPUT_FILE_TEST = 'output.txt'

######################## COMMAND LINE ARGUMENTS ########################

### Read in the input files as command-line arguments
###
def read_files():
    dictionary_file = postings_file = file_of_queries = file_of_output = None

    def usage():
        print ("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")
	
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-d':
            dictionary_file  = a
        elif o == '-p':
            postings_file = a
        elif o == '-q':
            file_of_queries = a
        elif o == '-o':
            file_of_output = a
        else:
            assert False, "unhandled option"

    if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
        usage()
        sys.exit(2)

    return dictionary_file, postings_file, file_of_queries, file_of_output

######################## DRIVER STATEMENTS ########################

def main():
    if len(sys.argv) <= 1:
        dictionary_file, postings_file, query_file, file_of_output = DICTIONARY_FILE_TEST, POSTINGS_FILE_TEST, QUERY_FILE_TEST, OUTPUT_FILE_TEST
    else:
        dictionary_file, postings_file, query_file, file_of_output = read_files()

    dictionary = get_dictionary(dictionary_file)
    document_properties = get_document_properties(DOCUMENT_PROPERTIES_FILE)

    with open(postings_file, 'rb') as p:
        query = get_query(query_file, dictionary)
        result = get_best_documents(p, dictionary, document_properties, query)

    with open(file_of_output, 'w') as f:
        f.write(' '.join([str(x) for x in result]) + END_LINE_MARKER)

if __name__ == "__main__":
    main()

#
#python search.py -d dictionary.txt -p postings.txt -q queries.txt -o output.txt


