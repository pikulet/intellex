from data_helper import *
from constants import *
from properties_helper import VECTOR_OFFSET
import math
import re
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk import pos_tag
import string

########################### DEFINE CONSTANTS ###########################

vector_post_file_handler = open(VECTOR_POSTINGS_FILE, 'rb')
document_properties = load_data(DOCUMENT_PROPERTIES_FILE)
total_num_documents = len(document_properties)

# debugging only
# def normalise_term(x):
#     return x

def idf_transform(x): return math.log(total_num_documents/x, 10)

AND = "AND"

stemmed_stopwords =  set([normalise_term(t) for t in stopwords.words('english')])
unstemmed_stopwords = stopwords.words('english')

punctuation = string.punctuation

######################## DRIVER FUNCTION ########################

def get_new_query_strings(line):
    """
    First Level Query Refinement Public Method
    This method takes a string as the input. This string should be the original query string that is fed into the program.
    The possible transformations available are:
    0. Positive list (not used here)
    1. + Phrase + Bool
    2. + Phrase - Bool
    3. - Phrase - Bool
    4. + Wordnet - Bool
    5. Rocchio relevance feedback (not used here)
    6. - Phrase + Bool

    A list of new query strings will be returned in the order of 034+6. 
    If any of the query strings are duplicated as a result of the transformation, only one of them will be inserted
    into the result.

    Bool Query Example:
    quiet AND "phone call" ->
    1 'quiet AND "phone call"',
    2 '"phone call" quiet', 
    3 'phone call quiet', 
    4 'smooth mute "quiet down" tranquil tranquillis still tranquil quiet subdu restrain hush placid tranquil quietli
    quieten placid tranquil "pipe down" repos tranquil silenc quiesc unruffl hush lull calm seren "calm down"
    "phone call" "telephon call" call'

    Free Text Query Example:
    quiet "phone call" ->
    1 'quiet AND "phone call"',
    2 'quiet "phone call"',
    3 'quiet phone call',
    4 'subdu mute tranquil tranquil tranquil hush smooth hush "quiet down" restrain calm still placid placid
    quietli quiesc silenc lull "pipe down" tranquillis seren repos unruffl "calm down" tranquil tranquil
    quiet quieten call "telephon call" "phone call"'

    Additional information:
    Wordnet finds the possible synonyms/hyponym of each term in the query string and puts all of them back into
    the query string.

    :param line: Query String to be expanded
    """
    if not isinstance(line, str):
        raise Exception("Wrong usage of method: query string should be a str")

    # This is the result to be returned
    result = []

    # Create tokens out of the query string
    is_bool, is_phrase, tokens = tokenize(line) # no distinct.
    stokens = filter_duplicates(tokens)     # distinct. No longer works with AND.

    ###### 3. NO PHRASE NO BOOL
    newlinelist = []
    for token in tokens:
        if token != AND:
            for subtoken in token.split():
                # if not (subtoken in unstemmed_stopwords):
                newlinelist.append(subtoken)

    result.append(convert_list_to_string(newlinelist))
    ######

    ##### 4. NO BOOL Wordnet Synonyms
    newlinelist = []
    count = 0
    for token in stokens:
        if token != AND:
            if token in unstemmed_stopwords:
                newlinelist.append(token)
            else:
                thesaurized = thesaurize_term(token) + [token]
                newlinelist += thesaurized
                if len(thesaurized) > 1:
                    count += len(thesaurized) - 1
    
    # Special trigger to switch Rocchio on if Wordnet is not useful
    if count < TRIGGER_ROCCHIO_LEVEL:
        import constants
        constants.EXPAND_QUERY = True
    result.append(convert_list_to_string(newlinelist, filter=True))
    #####

    
    ##### 1. Keep PHRASE Keep BOOL
    # result.append(convert_list_to_string(tokens))
    #####

    ###### 2. PHRASE NO BOOL (not used)
    # newlinelist = []
    # for token in tokens:
    #     if token != AND:
    #         newlinelist.append(token)
    # result.append(convert_list_to_string(newlinelist))

    # ###### 6. NO PHRASE BOOL (not used)
    # newlinelist = []
    # for token in tokens:
    #     if token != AND:
    #         for subtoken in token.split():
    #             newlinelist.append(subtoken)

    # newlinelist = intersperse(newlinelist, AND)
    # result.append(convert_list_to_string(newlinelist))
    # ######

    ###### 4.1 NO BOOL POS TAG Wordnet Synonyms (Not useful since the user's free text query can be quite bad)
    # newlinelist = []
    # tagged = pos_tag(tokens)
    # for word, pos in tagged:
    #     if word != AND:
    #         if word in unstemmed_stopwords:
    #             newlinelist.append(word)
    #         else:
    #             thesaurized = thesaurize_term_with_pos(word, pos) + [word]
    #             newlinelist += thesaurized
    # result.append(convert_list_to_string(newlinelist, filter=True))
    ######

    ##### 4.2 NO BOOL Wordnet Hynonyms (Too many terms returned and may explode)
    # newlinelist = []
    # for token in stokens:
    #     if token != AND:
    #         if token in unstemmed_stopwords:
    #             newlinelist.append(token)
    #         else:
    #             thesaurized = hyponymise_term(token) + [token]
    #             newlinelist += thesaurized
    # result.append(convert_list_to_string(newlinelist, filter=True))
    #####

    # Remove duplicates
    result = filter_duplicates(result)

    return result

######################## RELEVANCE FEEDBACK METHODS ########################

def get_new_query_vector(vector, docIDs):
    """
    Pseudo Relevance Feedback Public Method. This uses the Rocchio algorithm.
    This method takes in the original query vector and list of docIDs. 
    The query vector is modelled as sparse vector where it is a term -> score mapping. Zero scores are not stored too.
    The centroid from the list of docIDs will be calculated and added to original query vector. 
    Finally, the resulting vector is trimmed so that only the top k terms are returned
    :param vector: Original query vector
    :param docIDs: List of docIDs to get the centroid
    """
    # Guard methods
    if not isinstance(vector, dict):
        raise Exception("Wrong usage of method: vector should be a dict")

    if not isinstance(docIDs, list):
        raise Exception("Wrong usage of method: docIDs should be a list")

    offset = get_centroid_vector(docIDs)

    for key, value in vector.items():
        vector[key] = vector[key] * ROCCHIO_ORIGINAL_QUERY_WEIGHT

    for key, value in offset.items():
        vector[key] = vector.get(key, 0.) + value * ROCCHIO_CENTROID_WEIGHT

    return vector

def get_centroid_vector(docIDs):
    """
    Util Method which given a set of docIDs, returns the centroid of the document vectors.
    The document vectors are precomputed and stored in the document properties dictionary.
    A sparse dictionary of term to score mapping is returned.
    :param docIDs: List of docIDs to get the centroid
    """
    num_of_docs = len(docIDs)
    offset = {}
    for docID in docIDs:
        docID = int(docID)
        vector, normalisator = get_vector_from_docID_offset(
            document_properties[docID][VECTOR_OFFSET])
        for key, value in vector.items():
            normalised = extract_value(value) / normalisator
            offset[key] = offset.get(key, 0.) + normalised

    # Take average
    for k in offset.keys():
        offset[k] /= num_of_docs

    return trim_vector(offset)

def trim_vector(vector):
    """
    Since Rocchio will return a large vector, we will only return the top k terms.
    Stopwords and and punctuation are filtered from the top k terms.

    :param: vector: Sparse vector
    """
    new_vector = dict()
    number_of_terms_insert = 0
    from operator import itemgetter
    sort = sorted(vector.items(), key=itemgetter(1), reverse=True)
    for key, value in sort:
        if (not (key in stemmed_stopwords)) and (not (key in punctuation)):
            new_vector[key] = value
            number_of_terms_insert += 1
            if number_of_terms_insert >= ROCCHIO_TERMS:
                break

    return new_vector

def extract_value(tuple):
    """
    This method is to abstract away the format of vector.txt. Vector.txt keeps all vectors in a tf, df format.
    Currently, this method produces tfidf.

    :param: tuple: Tuple data that is saved inside vector.txt
    """
    return log_tf(tuple[0]) * idf_transform(tuple[1])

def get_vector_from_docID_offset(offset):
    """
    Given the docID offset, get the sparse vector from vector.txt
    :param: offset: integer offset of the sparse vector inside vector.txt
    """

    # vector are stored as sparse indexes
    # each valid index will map to (tf, idf)
    data = load_data_with_handler(vector_post_file_handler, offset)

    # we need to normalise
    normalisator = 0.
    for key, value in data.items():
        normalisator += extract_value(value) ** 2
    normalisator = math.sqrt(normalisator)

    return data, normalisator

######################## WORDNET EXPANSION METHODS ########################


def thesaurize_term(word):
    """
    Given a term t, returns an list of unique synonyms.
    If a term that has two words is given, the space will be replaced by a _ (This is the WordNet format)
    The resulting list will also have _ replaced back to space.
    :param: word: Word to be used against word
    """
    word = word.replace(" ", "_")
    terms = []
    for synset in wordnet.synsets(word):
        for item in synset.lemma_names():
            terms.append(item)

    return list(set(convert_wordnet_terms(terms)))


def thesaurize_term_with_pos(word, pos):
    """
    Similar to theasurize term, this method takes in the POS tag of the word,
    which helps wordnet to further reduce the number of terms returned
    :param: word: Word to be used against word
    :param: pos: POS Tag of the word
    """
    word = word.replace(' ', '_')
    terms = []
    for synset in wordnet.synsets(word, pos=get_wordnet_pos(pos)):
        for lemma in synset.lemmas():
            non_lemmatized = lemma.name().split('.', 1)[0].replace('_', ' ')
            terms.append(non_lemmatized)
    
    return (list(set(terms)))

def get_wordnet_pos(treebank_tag):
    """
    Util function to convert word tokenise's pos tags to wordnet pos tag
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return ''


def hyponymise_term(word):
    """
    Given a term t, return an list of unique hyponyms.
    If a term that has two words is given, the space will be replaced by a _ (This is the WordNet format)
    The resulting list will also have _ replaced back to space.
    :param: word: Word to be used against word
    """
    word = word.replace(" ", "_")
    terms = []
    for synset in wordnet.synsets(word):
        for item in synset.closure(lambda s: s.hyponyms()):
            terms += item.lemma_names()

    return list(set(convert_wordnet_terms(terms)))


def convert_wordnet_terms(terms):
    """
    Convert wordnet format back to normal terms such as replacing _ with spaces.
    Drops terms that are more than a triword
    :param: terms: List of terms in wordnet format
    """
    newterms = []
    for term in terms:
        term = term.replace("_", " ")
        if len(term.split()) > 2:
            pass
        newterms.append(term)
    return newterms

######################## UTIL FUNCTIONS ########################

def strip_query_to_free_text(line):
    """
    A really simple util function that strips out all boolean operators and phrase markings.
    :param: line: Query string
    """
    result = []
    b1, b2, tokens = tokenize(line)
    for token in tokens: 
        if token != AND:
            for subtoken in token.split():
                result.append(subtoken)
    return convert_list_to_string(result)    

def tokenize(line):
    """
    Tokenises a line to a list of words, using the delimiter as space or ".
    For example, the string 'quiet "phone call"' is converted to a list ['quiet', 'phone call'].
    Also returns is_bool and is_phrase to indicate if the line has boolean query or phrases respectively.
    :param: line: Query string
    """
    is_bool = False
    is_phrase = False
    line = " ".join(line.split())

    result = []

    temp = ""
    capture = False
    for c in line:
        if c == '"':
            is_phrase = True
            if capture == False:
                capture = True
            else:
                result.append(temp.strip())
                capture = False
                temp = ""
        elif c== " ":
            if capture:
                temp += c
                continue
            else:
                result.append(temp.strip())
                temp = ""
        else:
            temp += c
    
    result.append(temp.strip())
    result = list(filter(None, result))
    if "AND" in result:
        is_bool = True

    return is_bool, is_phrase, result

def intersperse(lst, item):
    """
    Util method which adds an item in-between every element in the list.
    :param lst: list to be modified
    :param item: item to be inserted
    """
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result

def filter_duplicates(line_list):
    """
    This method takes in a list of terms and removes the duplicated terms.
    :param line_list: List of tokens
    """
    tempresult = []
    tempresult_set = set()
    for i in line_list:
        if i in tempresult_set:
            pass
        else:
            tempresult.append(i)
            tempresult_set.add(i)

    return tempresult

def normalise_all_tokens_in_list(line_list):
    """
    This method takes in a list of terms and normalises each of them using case folding and stemming.
    A list of normalised terms are returned.
    :param: line_list: list of tokens
    """
    for i in range(len(line_list)):
        if line_list[i] == AND:
            continue
        line_list[i] = " ".join([normalise_term(x)
                                 for x in line_list[i].split()])
    return line_list

def convert_list_to_string(line_list, filter=False):
    """
    Util function which converts a list of tokens into string.
    If filter is true, duplicates are removed.
    Filter will remove also remove AND and cannot be used with boolean queries.
    :param: line_list: list of tokens
    :param: filter: enable removal of duplicates
    """
    result = ""

    # normalise all tokens first
    line_list = normalise_all_tokens_in_list(list(line_list))

    if filter:
        line_list = filter_duplicates(line_list)

    for line in line_list:
        if line == AND:
            result += line + " "
            continue
        subline = line.split()
        if len(subline) > 1:
            result += ' "'
            for s in subline:
                result += s + " "
            result = result[:-1]
            result += '" '
        else:
            result += line + ' '
    return result.strip().replace("  ", " ")


