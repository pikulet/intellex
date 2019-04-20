#!/usr/bin/python
import math
from properties_helper import CONTENT_LENGTH, BIGRAM_CONTENT_LENGTH, TRIGRAM_CONTENT_LENGTH, \
    TITLE_LENGTH,  BIGRAM_TITLE_LENGTH, TRIGRAM_TITLE_LENGTH

class Eval:
    '''
    A class which stores the dictionary, dictionary of document vector lengths and the total number of documents for
    evaluating queries. The main public function to be used is eval_query.
    '''

    def __init__(self, query, postings_lists, dictionary, document_properties, term_length=1, query_vector=None, is_title=False):
        '''
        Creates an Eval object.
        :param query: a list of terms, which may either be phrases (lists) or single terms.
        :param postings_lists: a list of postings lists, arranged in the same order as that in the query.
        :param dictionary: the dictionary mapping terms to (document frequency, pointer to postings lists) tuples.
        :param document_properties: the dictionary mapping docID to the document properties.
        :param term_length: the length of each term i.e. 1 if single term, 2 if biword, 3 if triword.
        :param query_vector: a precomputed query vector from relevance feedback.
        :param is_title: true if the query is to be searched within the title field.
        '''
        self.dictionary = dictionary
        self.document_properties = document_properties
        self.query_terms = query
        self.postings_lists = postings_lists
        self.N = len(document_properties)
        self.term_length = term_length
        self.query_vector = False
        self.is_title = is_title
        if query_vector is not None:
            self.query_vector = query_vector

    def eval_query(self):
        '''
        Evaluates a query and returns the top ten or fewer documents that match the query.
        This is done by:
        1. Creating a (truncated) query vector from the term list using get_query_vector. This is step is omitted if
        the vector has already been evaluated during relevance feedback expansion.
        2. Computing the cosine of the angle between the query vector and the vector of every document that
        appears in at least one postings list of the query terms using get_cosine_scores.
        4. Normalising the cosine scores with the document vector lengths (precomputed and stored).
        5. Storing each document to cosine score mapping in a dictionary to be returned.
        :param query: a list of terms in the query.
        :return: the top ten or fewer documents with the highest cosine scores.
        '''
        if self.query_vector:
            query_vector = self.query_vector
        else:
            query_vector = self.get_query_vector(self.query_terms)
        document_vectors = self.get_cosine_scores(query_vector)
        score_dict = {}
        for document in document_vectors:
            score = document_vectors[document]
            normalised_score = self.normalise(score, document)
            score_dict[int(document)] = normalised_score
        return score_dict

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

    def get_cosine_scores(self, query_vector):
        '''
        Retrieves the postings lists of all the terms in the query and compiles all the (docID, frequency) pairs
        into a dictionary of scores for each document, where each document ID maps to a cosine score. Each component of
        each document vector is converted from the raw term frequency to 1+log(tf). This is multiplied
        with the same term component of the query vector and directly added to the cosine score in the
        doc_score_dictionary. It is possible to ignore the components in the document vectors which do not appear
        in the query since in computing the cosine score, they evaluate to 0.
        :param query_vector: the query vector with tf-idf in each component.
        :return: a dictionary mapping document IDs to cosine scores, before normalisation.
        '''
        doc_score_dictionary = {}
        dimension = 0
        for posting_list in self.postings_lists:
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
        if df > 0:
            idf = math.log(self.N / df, 10)
        else:
            idf = 1
        return tf * idf

    def normalise(self, score, docID):
        '''
        Normalises a score by dividing by the normalisation factor i.e.
        the document vector length stored in the document_properties. As the document vector
        length differs according to the field (title and content) and length of the term
        (single word, biword or triword), the self.is_title and self.term_length attributes are
        used to retrieve the correct vector length from the document properties dictionary.
        :param score: the score before normalisation.
        :param docID: the docID of the document.
        :return: the normalised cosine score.
        '''
        if self.is_title:
            if self.term_length == 1:
                length = TITLE_LENGTH
            elif self.term_length == 2:
                length = BIGRAM_TITLE_LENGTH
            else:
                length = TRIGRAM_TITLE_LENGTH
        else:
            if self.term_length == 1:
                length = CONTENT_LENGTH
            elif self.term_length == 2:
                length = BIGRAM_CONTENT_LENGTH
            else:
                length = TRIGRAM_CONTENT_LENGTH

        normalisation_factor = self.document_properties[docID][length]
        normalised_score = score / normalisation_factor
        return normalised_score

def get_term_frequencies(query, dictionary):
    '''
    Creates and returns a list of (term, term frequency) tuples. Terms that are not in the dictionary are ignored.
    :param query: a list of terms in the query.
    '''
    term_frequencies = {}
    for term in query:
        if type(term) == list: # phrase queries
            term = tuple(term)
        elif term not in dictionary:
            continue
        if term not in term_frequencies:
            term_frequencies[term] = 0
        term_frequencies[term] += 1
    terms = list(term_frequencies.items())
    return terms