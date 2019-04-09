# [(docID, tf, []), ...]
# [(docID, tf, []), ...]
import math

DOC_ID_INDEX = 0
TF_INDEX = 1
POSTINGS_INDEX = 2

def get_docID(list, index):
    return list[index][DOC_ID_INDEX]

def has_skip(list, index, skip_dist):
    return index % skip_dist == 0

def get_skip_docID(list, index, skip_dist):
    return list[index + skip_dist][DOC_ID_INDEX]

def get_skip_position(list, index, skip_dist):
    return list[index + skip_dist]

def get_intersected_posting_lists(single, biword, triword):
    lists = single + biword + triword
    lists = sorted(lists, key = lambda x: x[0], reverse = True)
    common_doc_IDs = merge_n_lists(lists)
    reduced_single = list(map(lambda x: x[1], list(filter(lambda list: list[0] in common_doc_IDs, single))))
    reduced_biword = list(map(lambda x: x[1], list(filter(lambda list: list[0] in common_doc_IDs, biword))))
    reduced_triword = list(map(lambda x: x[1], list(filter(lambda list: list[0] in common_doc_IDs, triword))))
    return reduced_single, reduced_biword, reduced_triword

def merge_n_lists(lists):
    '''
    Returns the docIDs that occur in all lists.
    '''
    if len(lists) < 2:
        return lists
    merged_list = intersect(lists[0][1], lists[1][1], lists[0][0], lists[1][0])
    for i in range(2, len(lists)):
        merged_list = intersect(merged_list, lists[i][1], len(merged_list), lists[i][0])
    docID_list = list(map(lambda x: x[0], merged_list))
    return docID_list

def intersect(listA, listB, A_length, B_length):
    '''
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
            result.append(listA[i])
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

#lists = [[4, [(1,2), (2,3), (4,5), (5,6)]], [4, [(1,2), (2,3), (4,5), (5,6)]], [4, [(1,2), (2,3), (4,5), (5,6)]]]
#print(get_intersected_posting_lists(lists))