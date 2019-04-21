from search_helper import get_best_documents, load_data, get_query, relevance_feedback
import getopt
import sys
from constants import *
from QueryExpansion import get_new_query_strings, strip_query_to_free_text

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
    '''
    Main function for search loads in the dictionary and document properties file into memory and reads in
    the query file with the query string and the list of relevant documents known as the positive list.
    '''
    if len(sys.argv) <= 1:
        dictionary_file, postings_file, query_file, file_of_output = DICTIONARY_FILE_TEST, POSTINGS_FILE_TEST, QUERY_FILE_TEST, OUTPUT_FILE_TEST
    else:
        dictionary_file, postings_file, query_file, file_of_output = read_files()

    dictionary = load_data(dictionary_file)
    doc_properties = load_data(DOCUMENT_PROPERTIES_FILE)

    with open(postings_file, 'rb') as p:
        with open(query_file, 'r', encoding="utf-8") as f:
            query_data = f.read().splitlines()
        result = get_results(query_data, p, dictionary, doc_properties)

        with open(file_of_output, 'w+') as f:
            f.write(' '.join([str(x) for x in result]) + END_LINE_MARKER)

        if EXPAND_QUERY:
            query = strip_query_to_free_text(get_query(query_data[0]))
            relevant_docs = result[:NUM_DOCS_TO_FEEDBACK]
            extra_docs = relevance_feedback(p, dictionary, doc_properties, query, relevant_docs)
            extra_docs = list(filter(lambda x: x not in relevant_docs, extra_docs))
            relevant_docs += extra_docs

            with open(file_of_output, 'w+') as f:
                f.write(' '.join([str(x) for x in relevant_docs]) + END_LINE_MARKER)

def get_results(query_data, postings_handler, dictionary, doc_properties):
    '''
    Returns an ordered list of documents for the query.
    :param query_data:
    :param postings_handler:
    :param dictionary:
    :param doc_properties:
    '''
    original_query_string = query_data[0]
    queries = get_new_query_strings(original_query_string)

    positive_list = query_data[1:]
    result = [] + positive_list
    result_set = set(result)
    for query in queries:
        query = get_query(query)
        docs = get_best_documents(postings_handler, dictionary, doc_properties, query)
        docs = list(filter(lambda x: x not in result_set, docs))
        result_set = result_set.union(set(docs))
        result += docs
    return result

if __name__ == "__main__":
    import time
    start = time.time()
    main()
    end = time.time()
    print("Time Taken: %.5fs" % (end-start) )

#python search.py -d ../dictionary.txt -p ../postings.txt -q queries.txt -o output.txt
