from data_helper import *
from constants import *
from properties_helper import VECTOR_OFFSET
import math
import re
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk import pos_tag


########################### DEFINE CONSTANTS ###########################

vector_post_file_handler = open(VECTOR_POSTINGS_FILE, 'rb')
document_properties = load_data(DOCUMENT_PROPERTIES_FILE)
total_num_documents = len(document_properties)

# debugging only
# def normalise_term(x):
#     return x

def log_tf(x): return 1 + math.log(x, 10)

def idf_transform(x): return math.log(total_num_documents/x, 10)

AND = "AND"

stopwords =  set(stopwords.words('english'))

######################## DRIVER FUNCTION ########################


def get_new_query_strings(line):
    """
    First Level Query Refinement Public Method
    This method takes a str as the input. This str should be the original query string that is fed into the program.
    The possible transformations available are:
    1. Phrase + Bool
    2. Phrase - Bool
    3. - Phrase - Bool
    4. Wordnet - Bool
    A list of new query strings will be returned in the order of 1234. 
    If any of the query strings are duplicated as a result of the transformation, only one of them will be inserted into the result.

    Bool Query Example:
    quiet AND "phone call" ->
    1 'quiet AND "phone call"',
    2 '"phone call" quiet', 
    3 'phone call quiet', 
    4 'smooth mute "quiet down" tranquil tranquillis still tranquil quiet subdu restrain hush placid tranquil quietli quieten placid tranquil "pipe down" repos tranquil silenc quiesc unruffl hush lull calm seren "calm down" "phone call" "telephon call" call'
    Free Text Query Example:
    quiet "phone call" ->
    1 'quiet AND "phone call"',
    2 'quiet "phone call"',
    3 'quiet phone call',
    4 'subdu mute tranquil tranquil tranquil hush smooth hush "quiet down" restrain calm still placid placid quietli quiesc silenc lull "pipe down" tranquillis seren repos unruffl "calm down" tranquil tranquil quiet quieten call "telephon call" "phone call"'


    """
    print ("Original Query:")
    print (line)
    result = []

    is_bool, is_phrase, tokens = tokenize(line)
    stokens = list(set(tokens))     # no order and distinct

    if is_bool: # bool query

        ##### Original PHRASE BOOL
        result.append(convert_list_to_string(tokens))
        #####

        ###### PHRASE NO BOOL
        newlinelist = []
        for token in stokens:
            if token != AND:
                newlinelist.append(token)
        result.append(convert_list_to_string(newlinelist))


        ###### NO PHRASE NO BOOL
        if is_phrase:
            newlinelist = []
            for token in stokens:
                if token != AND:
                    for subtoken in token.split():
                        newlinelist.append(subtoken)
            result.append(convert_list_to_string(newlinelist))
        ######


    else: # free text

        ##### Original PHRASE NO BOOL
        result.append(convert_list_to_string(tokens))
        #####

        ###### PHRASE BOOL
        newlinelist = []
        for token in stokens:
            newlinelist.append(token)
            newlinelist.append(AND)
        newlinelist = newlinelist[:-1] # drop the last AND
        result.append(convert_list_to_string(newlinelist))


        ###### NO PHRASE NO BOOL
        if is_phrase:
            newlinelist = []
            for token in stokens:
                if token != AND:
                    for subtoken in token.split():
                        newlinelist.append(subtoken)
            result.append(convert_list_to_string(newlinelist))
        ######

        ######
        # ###### Original pos tag wordnet
        # newlinelist = []
        # tagged = pos_tag(tokens)
        # for word, pos in tagged:
        #     pos_in_wordnet = pos[0].lower()
        #     # ignore stopwords
        #     if word in stopwords:
        #         newlinelist += [word]
        #         continue

        #     symlist = []
        #     symlist.append(word) # add itself
        #     symlist += thesaurize_term_with_pos(word, pos_in_wordnet)
            
        #     newlinelist += symlist 
        #     ###

        # result.append(convert_list_to_string(newlinelist, filter=True))

    ##### Original no bool with Wordnet Sym
    newlinelist = []
    for token in tokens:
        if token != AND:
            thesaurized = hyponymise_term(token)
            if len(thesaurized) > 0:
                newlinelist += thesaurized
            else:
                newlinelist += [token]
        # else:
        #     newlinelist += [AND]
    result.append(convert_list_to_string(newlinelist))  # original query
    #####

    ######  Original no bool with Wordnet Hym
    # newlinelist = []
    # wordnet_used = 0
    # for token in stokens:
    #     if token != AND:
    #         thesaurized = hyponymise_term(token)
    #         if len(thesaurized) > 0:
    #             newlinelist += thesaurized
    #             wordnet_used += 1
    #         else:
    #             newlinelist += [token]
    # if wordnet_used > 0:
    #     result.append(convert_list_to_string(newlinelist, filter=True))
    ######

    
    ###### Original stripped stopwords
    # newlinelist = []
    # for token in tokens:
    #     if token != AND:
    #         if token in stopwords:
    #             # remember to drop the extra AND
    #             if len(newlinelist) > 0 and newlinelist[-1] == AND:
    #                 newlinelist = newlinelist[:-1]
    #             pass
    #         else:
    #             newlinelist += [token]
    #     else:
    #         # remember to drop the extra AND in front
    #         if len(newlinelist) == 0:
    #             continue
    #         newlinelist += [AND]
    # result.append(convert_list_to_string(newlinelist))
    ######


    print("New Query:")
    print(result)
    return result

def get_new_query_vector(vector, docIDs):
    """
    Relevance Feedback Public Method.

    This method takes in the original query vector and list of docIDs. 
    Note that The query vector is modelled as sparse vector where it is a term -> score mapping. Zero scores are not stored too.
    The centroid from the list of docIDs will be calculated and added to original query vector. 
    Finally, the resulting vector is trimmed so that terms that do not meet the mininum score is removed.
    """

    # Guard methods
    if not isinstance(vector, dict):
        raise Exception("Wrong usage of method: vector should be a dict")

    if not isinstance(docIDs, list):
        raise Exception("Wrong usage of method: docIDs should be a list")

    offset = get_new_query_offset(docIDs)
    for key, value in offset.items():
        vector[key] = vector.get(key, 0.) + value

    vector = trim_vector(vector)
    return vector

######################## UTIL FUNCTION ########################

# def thesaurize_term_with_pos(word, pos):
#     if (len(word.split()) >1 ):
#         word = word.replace(' ', '_')
#     for synset in wordnet.synsets(word, pos=pos):
#         for lemma in synset.lemmas():
#             non_lemmatized = lemma.name().split('.', 1)[0].replace('_', ' ')
#             yield non_lemmatized
        
def filter_duplicates(line_list):
    """
    This method takes in a list of terms and removes the duplicated terms. This is used for theasurize as multiple duplicates can be returned.
    """
    return list(dict.fromkeys(line_list)) 

def normalise_all_tokens_in_list(line_list):
    """
    This method takes in a list of terms and normalises each of them to the prefined normalised form.
    A list of normalised terms are returned.
    """
    for i in range(len(line_list)):
        if line_list[i] == AND:
            continue
        line_list[i] = " ".join([normalise_term(x)
                                 for x in line_list[i].split()])
    return line_list

def convert_list_to_string(line_list, filter=False):
    """
    Util function
    convert a list of tokens into string
    filter duplicates if turned on
    Note that filter will remove AND too, do not use this with bool query
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


def tokenize(line):
    """
    The line will be tokenised to a list of words, using the delimiter as space or "

    For example:
    quiet "phone call"
    ->
    quiet
    phone call

    Also returns is_bool and is_phrase to indicate if the line has boolean query or phrases respectively
    """
    is_bool = False
    is_phrase = False
    regex = re.compile('("\w* \w*")|(\w*)')
    result = []
    for group in regex.findall(line):
        for term in group:
            if term:
                if term == "AND":
                    is_bool = True
                if '"' in term:
                    is_phrase = True
                term = term.strip('"')
                result.append(term.strip())
    return is_bool, is_phrase, result


def thesaurize_term(t):
    """
    Given a term t, return an list of unique synonyms.
    If a term that has two words is given, the space will be replaced by a _ (This is the WordNet format)
    The resulting list will also have _ replaced back to space.
    """
    t = t.replace(" ", "_")
    terms = []
    for synset in wordnet.synsets(t):
        for item in synset.lemma_names():
            terms.append(item)

    return list(set(convert_wordnet_terms(terms)))

def hyponymise_term(t):
    """
    Given a term t, return an list of unique hyponyms.
    If a term that has two words is given, the space will be replaced by a _ (This is the WordNet format)
    The resulting list will also have _ replaced back to space.
    """
    t = t.replace(" ", "_")
    terms = []
    for synset in wordnet.synsets(t):
        for item in synset.closure(lambda s: s.hyponyms()):
            terms += item.lemma_names()

    return list(set(convert_wordnet_terms(terms)))


def convert_wordnet_terms(terms):
    """
    Remove some of the unuseable terms such as _
    """
    newterms = []
    for term in terms:
        term = term.replace("_", " ")
        newterms.append(term)
    return newterms


def trim_vector(vector):
    """
    Since Ricco will return a large vector, we will implement a min score for each term.
    Those terms that do not meet the point will be removed
    """
    new_vector = dict()
    for key, value in vector.items():
        if value > ROCCHIO_MIN_CUTOFF_POINT:
            new_vector[key] = value
    return new_vector


def extract_value(tuple):
    """
    Undated method. Will be removed soon.
    """
    return log_tf(tuple[0]) *\
        idf_transform(tuple[1])


def get_vector_from_docID_offset(offset):
    """
    Util Method
    Given the docID offset, get the vector dict
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


def get_new_query_offset(docIDs):
    """
    Util Method
    Given a set of docIDs, get the new offset to be used in the formula aka Centroid
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

    return offset