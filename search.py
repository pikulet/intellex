from index import normalise_term
from search_helper import *
from constants import *
import getopt
import sys
from properties_helper import get_document_properties
from constants import *

########################### DEFINE CONSTANTS ###########################

END_LINE_MARKER = '\n'

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

    dictionary = load_data(dictionary_file)
    doc_properties = load_data(DOCUMENT_PROPERTIES_FILE)

    for i in range(NUM_QUERIES_IN_FILE):
        with open(postings_file, 'rb') as p:
            with open(query_file, 'r', encoding="utf-8") as f:
                query_data = f.read().splitlines()

            query = get_query(query_data, query_line=i, multiple_queries=MULTIPLE_QUERIES_IN_FILE)
            result = get_best_documents(p, dictionary, doc_properties, query)

            if NO_PHRASES and "\"" in query_data[i]:
                query2 = get_query(query_data, query_line=i, multiple_queries=MULTIPLE_QUERIES_IN_FILE, no_phrases=NO_PHRASES)
                result2 = get_best_documents(p, dictionary, doc_properties, query2)
                result = list(filter(lambda x: x not in result2, result))
                result = result2 + result

        with open(file_of_output, 'w+') as f:
            f.write(' '.join([str(x) for x in result]) + END_LINE_MARKER)

        if EXPAND_QUERY:
            with open(postings_file, 'rb') as p:
                with open(query_file, 'r', encoding="utf-8") as f:
                    query_data = f.read().splitlines()
                query = get_query(query_data, query_line=i, multiple_queries=MULTIPLE_QUERIES_IN_FILE)
                positive_list = query[1:] if not MULTIPLE_QUERIES_IN_FILE else []
                relevant_docs = positive_list + result
                extra_docs = expand_query(p, dictionary, doc_properties, query, relevant_docs)
                extra_docs = list(filter(lambda x: x not in relevant_docs, extra_docs))
                relevant_docs += extra_docs

            with open(file_of_output, 'w+') as f:
                f.write(' '.join([str(x) for x in relevant_docs]) + END_LINE_MARKER)

if __name__ == "__main__":
    import time
    start = time.time()
    main()
    end = time.time()
    print("Time Taken: %.5fs" % (end-start) )

#python search.py -d ../dictionary.txt -p ../postings.txt -q queries.txt -o output.txt
