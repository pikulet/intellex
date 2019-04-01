#!/usr/bin/python
import re
import sys
import getopt
import math
import nltk
import heapq

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def main():
    '''
    Main function reads in the dictionary file into memory, then processes each query in the query file,
    writing the evaluated output to the output file line by line.
    Reads in a dictionary which maps terms to document frequencies and pointers to the postings lists of each term,
    a length_dictionary which maps documents to the length of the document vector for normalisation,
    and the total number of documents, used for computing idf.
    '''
    query_file = open(file_of_queries, "r")
    open(output_file_of_results, "w").close()
    output = open(output_file_of_results, 'a')
    dictionary = read_dictionary()
    length_dictionary = read_document_lengths()
    N = get_num_documents()
    eval = Eval(dictionary, length_dictionary, N)
    for line in query_file:
        query = process_query(line)
        try:
            postings = eval.eval_query(query)
        except:
            postings = []
        output.write(print_output(postings) + "\n")


def process_query(line):
    '''
    Processes a raw query string into tokenised query terms. Each term is case folded and stemmed.
    :param line: The raw query as a string.
    :return: A list of query terms.
    '''
    query = line[:-1] if line[-1] == "\n" else line
    tokenised_query = query.split()
    query_terms = []
    stemmer = nltk.stem.porter.PorterStemmer()
    for term in tokenised_query:
        term = term.lower()
        term = stemmer.stem(term).strip()
        query_terms.append(term)
    return query_terms


def print_output(list):
    '''
    Converts a list into a string to be written to output.
    '''
    string = ""
    for docID in list:
        string += docID + " "
    return string[:-1]


def read_dictionary():
    '''
    Reads the dictionary file into a dictionary mapping each term to a (frequency, term_pointer) tuple.
    '''
    dictionary = {}
    file = open(dictionary_file, "r")
    for line in file:
        line = line[:-1]
        entry = line.split()
        word = entry[0]
        freq = int(entry[1])
        pointer = int(entry[2])
        dictionary[word] = (freq, pointer)
    return dictionary


def read_document_lengths():
    '''
    Reads in the file containing the vector lengths/magnitude of each document used to normalise the vector.
    Creates a dictionary which maps document IDs to the vector lengths.
    '''
    length_dictionary = {}
    file = open(normalisation_file, "r")
    for line in file:
        line = line[:-1]
        entry = line.split()
        if len(entry) < 2:
            continue
        word = entry[0]
        length = float(entry[1])
        length_dictionary[word] = length
    return length_dictionary


def get_num_documents():
    '''
    Reads and returns the total number of documents in the collection, stored in the first line of the file containing
    vector lengths for normalisation.
    '''
    file = open(normalisation_file, "r")
    file.seek(0)
    num_docs = int(file.readline())
    return num_docs


class Eval:
    '''
    A class which stores the dictionary, dictionary of document vector lengths and the total number of documents for
    evaluating queries.
    '''

    def __init__(self, dictionary, length_dictionary, N):
        '''
        Creates an Eval object.
        :param dictionary: the dictionary mapping terms to (document frequency, pointer to postings lists) tuples.
        :param length_dictionary: the dictionary mapping documents to the length of each document vector.
        :param N: the total number of documents.
        '''
        self.dictionary = dictionary
        self.length_dictionary = length_dictionary
        self.N = N

    def get_postings_list(self, term):
        '''
        Reads in the postings list of a term as a list of pairs represented as a list of two elements:
        the document ID and the term frequency associated with that document ID. The pointer in the dictionary
        is used to seek to the byte address of the postings list in the postings file.
        '''
        pointer = self.dictionary[term][1]
        file = open(postings_file, "r")
        file.seek(pointer)
        postings = file.readline().split()
        postings_list = []
        for pair in postings:
            posting = pair.split(",")
            posting[1] = int(posting[1])
            postings_list.append(posting)
        return postings_list

    def eval_query(self, query):
        '''
        Evaluates a query and returns the top ten or fewer documents that match the query.
        This is done by:
        1. Creating a list of (term, term frequency) tuples using get_term_frequencies.
        2. Creating a (truncated) query vector from the term list using get_query_vector.
        3. Computing the cosine of the angle between the query vector and the vector of every document that
        appears in at least one postings list of the query terms using get_cosine_scores.
        4. Normalising the cosine scores with the document vector lengths (precomputed and stored).
        5. Selecting the top ten documents with the highest cosine values using a min heap and negated scores, ensuring
        that documents with the same score are ordered by document ID.
        :param query: a list of terms in the query.
        :return: the top ten or fewer documents with the highest cosine scores.
        '''
        terms = self.get_term_frequencies(query)
        query_vector = self.get_query_vector(terms)
        document_vectors = self.get_cosine_scores(terms, query_vector)
        score_list = []
        for document in document_vectors:
            score = document_vectors[document]
            normalised_score = self.normalise(score, document)
            score_list.append((-normalised_score, int(document)))

        top_results = heapq.nsmallest(10, score_list, key=lambda x: (x[0], x[1]))  # smallest since min_heap is used
        top_documents = list(map(lambda x: str(x[1]), top_results))
        return top_documents

    def get_term_frequencies(self, query):
        '''
        Creates and returns a list of (term, term frequency) tuples. Terms that are not in the dictionary are ignored.
        :param query: a list of terms in the query.
        '''
        term_frequencies = {}
        for term in query:
            if term not in self.dictionary:
                continue
            if term not in term_frequencies:
                term_frequencies[term] = 0
            term_frequencies[term] += 1
        terms = list(term_frequencies.items())
        return terms

    def get_query_vector(self, query_terms):
        '''
        Creates a truncated query vector by computing the td-idf for each component.
        The full query vector should rightly have the same dimension as every document vector,
        which is the number of unique terms in the dictionary. However, since when computing cosine scores,
        components with 0 tf-idf in the query vector evaluate to 0, they have no effect and are hence
        not stored in this implementation. The list returned here hence stores only as many components
        as the number of unique terms in the query.
        The query vector is not normalised since normalisation has the same effect on the
        final cosine score when comparing against each document.
        :param query_terms: a list of (term, term frequency) tuples
        :return: a query vector
        '''
        vector = []
        for term in query_terms:
            tf = term[1]
            df = self.dictionary[term[0]][0]
            tf_idf = self.get_tf_idf(tf, df)
            vector.append(tf_idf)
        return vector

    def get_cosine_scores(self, query_terms, query_vector):
        '''
        Retrieves the postings lists of all the terms in the query and compiles all the (docID, frequency) pairs
        into a dictionary of scores for each document, where each document ID maps to a cosine score. Each component of
        each document vector is converted from the raw term frequency to 1+log(tf). This is multiplied
        with the same term component of the query vector and directly added to the cosine score in the
        doc_score_dictionary. It is possible to ignore the components in the document vectors which do not appear
        in the query since in computing the cosine score, they evaluate to 0.
        :param query_terms: a list of (term, term frequency) tuples
        :param query_vector: the query vector with tf-idf in each component.
        :return: a dictionary mapping document IDs to cosine scores, before normalisation.
        '''
        postings_lists = list(map(lambda x: self.get_postings_list(x[0]), query_terms))
        doc_score_dictionary = {}
        dimension = 0
        for posting_list in postings_lists:
            for posting in posting_list:
                docID = posting[0]
                freq = posting[1]
                if docID not in doc_score_dictionary:
                    doc_score_dictionary[docID] = 0
                doc_score_dictionary[docID] += self.get_log_tf(freq) * query_vector[dimension]
            dimension += 1
        return doc_score_dictionary

    def get_log_tf(self, tf):
        '''
        Given the term frequency, return the log tf using the formula 1 + log(tf).
        '''
        tf = 1 + math.log(tf, 10)
        return tf

    def get_tf_idf(self, tf, df):
        '''
        Returns the tf_idf given the term frequency (tf) and the document frequency (df).
        '''
        tf = 1 + math.log(tf, 10)
        idf = math.log(self.N / df, 10)
        return tf * idf

    def normalise(self, score, document):
        '''
        Normalises a score by dividing by the normalisation factor i.e.
        the document vector length stored in the length_dictionary.
        :param score: the score before normalisation.
        :param document: the docID of the document.
        :return: the normalised cosine score.
        '''
        normalisation_factor = self.length_dictionary[document]
        normalised_score = score / normalisation_factor
        return normalised_score

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError as err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        output_file_of_results = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or output_file_of_results == None:
    usage()
    sys.exit(2)

normalisation_file = "normalisation.txt"
main()