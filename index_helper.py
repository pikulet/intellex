#!/usr/bin/python
import math
from data_helper import *
try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda *i, **kwargs: i[0]

########################### DEFINE CONSTANTS ###########################


log_tf = lambda x: 1 + math.log(x, 10)


########################### CONTENT PROCESSING ###########################


### Process a document content body directly (content must be a list of normalized terms)
###
def process_doc_vector_and_bigram_trigram(docID, content, dictionary, postings):
    vector = dict()                 # term vector for this document
    biword_vector = dict()         # biword vector for this document
    triword_vector = dict()        # triword vector for this document

    position_counter = 0
    biword_flag = ""
    triword_flag = ["", ""]

    for t in content:
        add_data(docID, t, position_counter, dictionary, postings)
        add_vector_count(t, vector)
        add_vector_count((biword_flag, t), biword_vector)
        add_vector_count((triword_flag[0], triword_flag[1], t), triword_vector)

        # after storing, move the flag
        biword_flag = t
        triword_flag[0] = triword_flag[1]
        triword_flag[1] = t
        position_counter += 1   

    convert_tf(vector)
    convert_tf(biword_vector)
    convert_tf(triword_vector)

    return vector, biword_vector, triword_vector

### Add information about term and position to dictionary and posting list
###
def add_data(docID, t, position, dictionary, postings):
    if dictionary.has_term(t):
        termID = dictionary.get_termID(t)
        added_new_docID = postings.add_position_data(termID, docID, position)
        
        if added_new_docID:
            dictionary.add_df(t)

    else:
        termID = postings.add_new_term_data(docID, position)
        dictionary.add_term(t, termID)      

### Add the term count to the vector, for calculating document length
###
def add_vector_count(t, vector):
    if t in vector:
        vector[t] += 1
    else:
        vector[t] = 1

### Convert a content vector to tf-form for calculating document length
###
def convert_tf(vector):
    for t, tf in vector.items():
        vector[t] = log_tf(tf)

### Calculate the length of a vector
###
def get_length(vector):
    return math.sqrt(sum(map(lambda x: x**2, vector.values())))

########################## HELPER DATA STRUCTURES ##########################
    
### A dictionary class that keeps track of terms --> document_frequency/ idf, termID/ term_offset
### termID is a sequential value to access the posting list of the term at indexing time
### term_offset is the exact position (in bytes) of the term posting list in postings.txt
###
class Dictionary():

    DF = 0
    IDF = 0
    TERMID = 1
    TERM_OFFSET = 1
    
    def __init__(self, file):
        self.terms = {} # every term maps to a tuple of document_frequency/idf, termID/ term_offset
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

    def save_to_disk(self, total_num_documents):
        self.total_num_documents = total_num_documents

        store_data(self.file, self)
    

### A Postings class that collects all the posting lists.
### Each posting list is a dictionary mapping docIDs to term frequencies
###
class PostingList():

    DOC_ID = None
    TF = 0
    POSITION_LIST = 1
    
    def __init__(self, file):
        self.file = file
        self.postings = []
        self.currentID = -1

    def add_new_term_data(self, docID, position):
        new_posting = { docID : [1, [position] ] }
        self.postings.append(new_posting)

        self.currentID += 1
        return self.currentID       # return the index of the new posting list (termID)

    # Create a new entry in the posting list
    # Returns true if a new docID was added
    def add_position_data(self, termID, docID, position):
        term_posting = self.postings[termID]

        if docID in term_posting:
            doc_posting = term_posting[docID]
            doc_posting[PostingList.TF] += 1
            doc_posting[PostingList.POSITION_LIST].append(position)
            return False
        else:
            term_posting[docID] = [1, [position] ]
            return True

    # Returns a new posting entry format
    def get_new_posting(self, docID, position):
        return { docID : [1, [position] ] }         # tf, list(postiions)

    # Converts a dictionary { docID: [tf, [positions]] } to a sorted list of [docID, tf, [positions]]
    def flatten(self, posting):
        sorted_list = list()
        for docID in sorted(posting):
            new_entry = [docID] + posting[docID]
            sorted_list.append(new_entry)

        # This is the new indexes
        # PostingList.DOC_ID = 0
        # PostingList.TF = 1
        # PostingList.POSITION_LIST = 2
        
        return sorted_list

    # Saves the posting lists to file, and update offset value in the dictionary
    def save_to_disk(self, dictionary):        
        with open(self.file, 'wb') as f:
            for t in tqdm(dictionary.get_terms(), total=len(dictionary.get_terms())):
                termID = dictionary.get_termID(t)
                posting = self.postings[termID]
                posting = self.flatten(posting)     # convert dict to sorted list

                dictionary.set_offset(t, f.tell())  # update dictionary with current byte offset
                store_data_with_handler(f, posting)
