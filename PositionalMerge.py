# [(docID, tf, []), ...]
# [(docID, tf, []), ...]
import math

DOC_ID_INDEX = 0
TF_INDEX = 1
POSTINGS_INDEX = 2

def get_docID(list, index):
    return list[index][DOC_ID_INDEX]

def has_skip(list, index, skip_dist):
    return index + skip_dist < len(list) and index % skip_dist == 0

def get_skip_docID(list, index, skip_dist):
    return list[index + skip_dist][DOC_ID_INDEX]

def get_skip_position(list, index, skip_dist):
    return list[index + skip_dist]

def get_postings_from_phrase(phrase, postings_lists):
    '''
    Returns a postings list where each posting is a (docID, tf) tuple for the given phrase.
    The algorithm goes through the phrase and performs two-way merge for each contiguous pair in phrase.
    The results of the pairwise merge are appended to a merge_results dictionary, which is later processed to ensure
    that the pairs are contiguous.
    :param phrase: a list of either 2 or 3 terms (biword or triword).
    :param postings_lists: the postings lists for each term in the phrase in order, where each posting is in the form
    [docID, tf, position list].
    '''
    all_results = []
    merge_results = {}
    for i in range(len(phrase)-1):
        postings_list_A = postings_lists[i]
        postings_list_B = postings_lists[i+1]
        df_A = len(postings_list_A)
        df_B = len(postings_list_B)
        docs = intersect_lists(postings_list_A, postings_list_B, df_A, df_B)
        all_results += docs
        for doc in docs:
            if doc[0] not in merge_results:
                merge_results[doc[0]] = []
            merge_results[doc[0]].append(doc[1])
    for doc in merge_results:
        merge_results[doc] = len(merge_n_position_lists(merge_results[doc]))
    return list(merge_results.items())

def intersect_lists(listA, listB, A_length, B_length):
    '''
    Merges two lists of the form [docID, tf, position list] by first merging by docID.
    When the same docID is encountered in both lists, the intersect_position_lists function is called
    to merge the position lists and find positions which start the phrase.
    Skip pointers are dynamically generated based on the length of the lists.
    Returns a list of (docID, position list) tuples.
    '''
    result = []
    i, j = 0, 0
    skip_dist_A = int(math.sqrt(A_length))
    skip_dist_B = int(math.sqrt(B_length))
    while i < A_length and j < B_length:
        docID_A = get_docID(listA, i)
        docID_B = get_docID(listB, j)
        if docID_A == docID_B:
            positions = intersect_postion_lists(listA[i][POSTINGS_INDEX], listB[j][POSTINGS_INDEX],
                                                listA[i][TF_INDEX], listB[j][TF_INDEX])
            if positions:
                result.append((docID_A, positions))
            i += 1
            j += 1
        elif docID_A < docID_B:
            if has_skip(listA, i, skip_dist_A) and get_skip_docID(listA, i, skip_dist_A) <= docID_B:
                while has_skip(listA, i, skip_dist_A) and get_skip_docID(listA, i, skip_dist_A) <= docID_B:
                    i += skip_dist_A
            else:
                i += 1
        elif docID_A > docID_B:
            if has_skip(listB, j, skip_dist_B) and get_skip_docID(listB, j, skip_dist_B) <= docID_A:
                while has_skip(listB, j, skip_dist_B) and get_skip_docID(listB, j, skip_dist_B) <= docID_A:
                    j += skip_dist_B
            else:
                j += 1
    return result

def intersect_postion_lists(listA, listB, A_length, B_length):
    '''
    Returns the intersection of listA and listB, both of which are positional lists.
    For a positional index x to be appended to the final result, the position x must be in listA
    while x+1 must be found in listB.
    '''
    result = []
    i, j = 0, 0
    skip_dist_A = int(math.sqrt(A_length))
    skip_dist_B = int(math.sqrt(B_length))
    while i < A_length and j < B_length:
        pos_A = listA[i]
        pos_B = listB[j]
        if pos_A == pos_B - 1:
            result.append(pos_A)
            i += 1
            j += 1
        elif pos_A < pos_B - 1:
            if has_skip(listA, i, skip_dist_A) and get_skip_position(listA, i, skip_dist_A) <= pos_B:
                while has_skip(listA, i, skip_dist_A) and get_skip_position(listA, i, skip_dist_A) <= pos_B:
                    i += skip_dist_A
            else:
                i += 1
        elif pos_A > pos_B - 1:
            if has_skip(listB, j, skip_dist_B) and get_skip_position(listB, j, skip_dist_B) <= pos_A:
                while has_skip(listB, j, skip_dist_B) and get_skip_position(listB, j, skip_dist_B) <= pos_A:
                    j += skip_dist_B
            else:
                j += 1
    return result

def merge_n_position_lists(position_lists):
    '''
    Takes in n position lists which are the output of two-way pair merges.
    Returns the starting position for phrases which are contiguous.
    '''
    first_list = position_lists[0]
    results = []
    for pos in first_list:
        all_match = True
        for pos_list in range(1, len(position_lists[1:])):
            if pos + pos_list not in position_lists[pos_list]:
                all_match = False
                break
        if all_match:
            results.append(pos)
    return results