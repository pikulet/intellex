from data_helper import store_data_with_handler
try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda *i, **kwargs: i[0]
# tqdm = lambda *i, **kwargs: i[0] # this is to disable tqdm


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
