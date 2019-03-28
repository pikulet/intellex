#!/usr/bin/python
import math
import nltk
from nltk.stem.porter import *
import pickle

########################### DEFINE CONSTANTS ###########################
PORTER_STEMMER = PorterStemmer()
END_LINE_MARKER = '\n'

########################### CONTENT PROCESSING ###########################

### Normalise a term
###
def normalise_term(t):
    return PORTER_STEMMER.stem(t.lower())

### Process a document content body
###
def process_doc(docID, content, dictionary, postings, length):
    vector = dict()                 # term vector for this document
    position_counter = 0
    
    for l in content.split(END_LINE_MARKER):
        position_counter = process_line(docID, l, position_counter, vector, dictionary, postings)            

    convert_tf(vector)
    length[docID] = get_length(vector)
    
### Process a line in a document
###
def process_line(docID, line, position, vector, dictionary, postings):
    sentences = nltk.sent_tokenize(line)

    for s in sentences:
        words = nltk.word_tokenize(s)
        for w in words:
            t = normalise_term(w)

            add_data(docID, t, position, dictionary, postings)
            add_vector_count(t, vector)
                
            position += 1

    return position

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
    log_tf = lambda x: 1 + math.log(x, 10)
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
        with open(self.file, 'wb') as f:
            pickle.dump(self.terms, f)

### A Postings class that collects all the posting lists.
### Each posting list is a dictionary mapping docIDs to term frequencies
###
class PostingList():

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
            
    # Saves the posting lists to file, and update offset value in the dictionary
    def save_to_disk(self, length, dictionary):        
        with open(self.file, 'wb') as f:
            pickle.dump(length, f)

            for t in dictionary.get_terms():
                termID = dictionary.get_termID(t)
                posting = self.postings[termID]

                dictionary.set_offset(t, f.tell())  # update dictionary with current byte offset
                pickle.dump(posting, f)
