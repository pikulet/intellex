import pickle
from index import Dictionary, PostingList

########################### DEFINE CONSTANTS ###########################
CONJUNCTION_OPERATOR = " AND "
PHRASE_MARKER = "\""
INVALID_TERM_IDF = -1

######################## FILE READING FUNCTIONS ########################

### Retrieve a dictionary mapping docIDs to normalised document lengths
###
def get_lengths(p):
    p.seek(0)
    length_dict = pickle.load(p)
    return length_dict

### Retrieve a dictionary format given the dictionary file
###
def get_dictionary(dictionary_file):
    with open(dictionary_file, 'rb') as f:
        dictionary = pickle.load(f)
    return dictionary

### Retrieve a query format given the query file
###
def get_query(query_file):
    with open(query_file, 'r') as f:
        data = f.read().splitlines()

    query_text = parse_query(data[0])
    positive_list = [int(x) for x in data[1:] ]
    return query_text, positive_list

### Retrieve the posting list for a particular term
###
def get_posting(p, dictionary, t):
    try:
        term_data = dictionary[t]
        idf = term_data[Dictionary.IDF]
        
        offset = term_data[Dictionary.TERM_OFFSET]
        p.seek(offset)
        data = pickle.load(p)
        return idf, data
    except KeyError:
        # Term does not exist in dictionary
        return INVALID_TERM_IDF, list()
    
######################## QUERY PROCESSING ########################

### Parse the free-text query for AND operators and phrases (" ")
### "fertility treatment" AND damages --> [ ['fertility', 'treatment'], 'damages']
###
def parse_query(q):
    q = q.split(CONJUNCTION_OPERATOR)
    is_phrase = lambda s: s.startswith(PHRASE_MARKER)
    parse_phrase = lambda s: s[1: -1].split()

    result = list()
    for t in q:
        if is_phrase(t):
            result.append(parse_phrase(t))
        else:
            result.extend(t.split())
    return result

def process_query(p, dictionary, q):
    lengths = get_lengths(p)
    
    return list()


