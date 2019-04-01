
from search_helper import Dictionary, PostingList, parse_query

topk = 5
n = 20

def parse_query_with_expander(query):
    result = parse_query(query)
    if len(result) > n:
        pass
    else:
        # do something
        # result needs to keep the original tf-idf vectors of the documents
        new_query = []
        docs = result[:topk]

        # add up all of the topk
        for i in docs:
            for dimen in range(len(i)):
                if len(new_query) <= dimen:
                    new_query[dimen] = i[dimen]
                else:
                    new_query.append(i[dimen])

        # take the average
        for dimen in range(len(new_query)):
            new_query[dimen] = new_query[dimen] / topk

        # run the query again?
        # new_results = parse_query_as_vector(new_query)
        new_results = parse_query(new_query)
        result.extend(new_results[:topk])

    return result
