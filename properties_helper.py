import datetime as dt
from data_helper import load_data

### Retrieve a dictionary mapping docIDs to normalised document lengths
###
def get_document_properties(properties_file):
    document_properties = load_data(properties_file)
    return document_properties

########################### DEFINE CONSTANTS ###########################

# docID --> [content_length, title_length, court_priority, date_posted, vector_offset, bigram_normalise_Factor, trigram_normalise_Factor]
# Every property is assigned an index in the list of document properties
NUM_DOCUMENT_PROPERTIES = 9
CONTENT_LENGTH, TITLE_LENGTH, COURT_PRIORITY, DATE_POSTED, VECTOR_OFFSET, BIGRAM_CONTENT_LENGTH, TRIGRAM_CONTENT_LENGTH, BIGRAM_TITLE_LENGTH, TRIGRAM_TITLE_LENGTH = list(range(NUM_DOCUMENT_PROPERTIES))

COURT_HIERARCHY = {
    "SG Court of Appeal"                        : 1,
    "SG Privy Council"                          : 1,
    "UK House of Lords"                         : 1,
    "UK Supreme Court"                          : 1,
    "High Court of Australia"                   : 1,
    "CA Supreme Court"                          : 1,
    "SG High Court"                             : 2,
    "Singapore International Commercial Court"  : 2,
    "HK High Court"                             : 2,
    "HK Court of First Instance"                : 2,
    "UK Crown Court"                            : 2,
    "UK Court of Appeal"                        : 2,
    "UK High Court"                             : 2,
    "Federal Court of Australia"                : 2,
    "NSW Court of Appeal"                       : 2,
    "NSW Court of Criminal Appeal"              : 2,
    "NSW Supreme Court"                         : 2
    }

CURRENT_TIME = dt.datetime.now()

########################### SETTER METHODS ###########################

document_properties = dict()

def create_empty_property_list(docID):
    document_properties[docID] = list(range(NUM_DOCUMENT_PROPERTIES))

def assign_property(docID, property_index, value):
    document_properties[docID][property_index] = value

def update_court(docID, new_priority):
    # only the highest court priority (smallest priority number) is saved
    document_properties[docID][COURT_PRIORITY] = min(document_properties[docID][COURT_PRIORITY], new_priority)

########################### PROCESSING METHODS ###########################

def get_court_priority(court):
    return COURT_HIERARCHY.get(court, 3)

def get_recent_level(timestamp):
    difference = CURRENT_TIME - timestamp
    return difference.total_seconds()
