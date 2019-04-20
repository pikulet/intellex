from data_helper import store_data

'''
A dictionary class that keeps track of terms --> document_frequency/ idf, termID/ term_offset.
termID is a sequential value to access the posting list of the term at indexing time
term_offset is the exact position (in bytes) of the term posting list in postings.txt
'''
class Dictionary():

    DF = 0
    IDF = 0
    TERMID = 1
    TERM_OFFSET = 1

    def __init__(self, file):
        self.terms = {}  # every term maps to a tuple of document_frequency/idf, termID/ term_offset
        self.file = file
        self.total_num_documents = 0

    def has_term(self, t):
        return t in self.terms

    def get_termID(self, t):
        return self.terms[t][Dictionary.TERMID]

    def add_term(self, t, termID):
        self.terms[t] = [1, termID]

    def get_terms(self):
        return self.terms

    def add_df(self, t):
        self.terms[t][Dictionary.DF] += 1

    def set_idf(self, t, idf):
        self.terms[t][Dictionary.IDF] = idf

    def set_offset(self, t, offset):
        self.terms[t][Dictionary.TERM_OFFSET] = offset

    def save_to_disk(self):
        store_data(self.file, self.terms)
