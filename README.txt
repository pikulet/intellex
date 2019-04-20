This is the README file for the submission of
A0172868M-A0171426J-A0168355W-A0164816Y

e0202438@u.nus.edu
e0200996@u.nus.edu
e0176788@u.nus.edu
e0148858@u.nus.edu

== Python Version ==

We're using Python Version <3.6> for this assignment.

== General Notes about this assignment ==

# Analysis of the Corpus

A short corpus analysis is done. https://notebooks.azure.com/jason-soh/projects/homework4/html/index.ipynb
- 17137 documents
- 31 types of courts in the court field
- All field are populated

- Duplicated document id (?)
67          247336  ...               HK Court of First Instance
68          247336  ...                            HK High Court
109        2044863  ...               HK Court of First Instance
110        2044863  ...                            HK High Court
248        2145566  ...               Federal Court of Australia
249        2145566  ...  Industrial Relations Court of Australia
348        2147493  ...               Federal Court of Australia
349        2147493  ...  Industrial Relations Court of Australia
392        2148198  ...               Federal Court of Australia
393        2148198  ...  Industrial Relations Court of Australia
1207       2167027  ...               Federal Court of Australia
1208       2167027  ...  Industrial Relations Court of Australia
1554       2225321  ...                       UK Court of Appeal
1555       2225321  ...                           UK Crown Court
1565       2225341  ...                            UK High Court
1566       2225341  ...                           UK Crown Court
1638       2225516  ...                       UK Court of Appeal
1639       2225516  ...                            UK High Court
1672       2225597  ...                       UK Court of Appeal
1673       2225597  ...                            UK High Court
1674       2225598  ...                       UK Court of Appeal
1675       2225598  ...                            UK High Court
14027      3062427  ...               Federal Court of Australia
14028      3062427  ...  Industrial Relations Court of Australia
14029      3062433  ...               Federal Court of Australia
14030      3062433  ...  Industrial Relations Court of Australia
14036      3063259  ...               Federal Court of Australia
14037      3063259  ...  Industrial Relations Court of Australia
14039      3063522  ...               Federal Court of Australia
14040      3063522  ...  Industrial Relations Court of Australia
14638      3926753  ...                       UK Court of Appeal
14639      3926753  ...                           UK Crown Court
- Chinese documents from HK High Court and HK Court of First Instance (duplicated)
2044863
- Possible other unicode characters but can be easily resolved with utf-8 encoding

# Indexing Algorithm

## Parallelising NLTK tokenisation

## Storing biword and triword information

# Searching Algorithm

### need to finalise and explain overall approach.

Query expansion is done to the original query string to produce multiple versions of the same query (see section on
query expansion). Every query can one of the following four types:

1. +phrase, + boolean: e.g. "fertility treatment" AND damages
2. +phrase, -boolean: e.g. "fertility treatment" damages
3. -phrase, +boolean: e.g. fertility AND treatment AND damages
4. -phrase, -boolean: e.g. fertility treatment damages (basic free text query without phrases or boolean operator)

For an original query string with both phrases and the "AND" boolean operator, query expansion can allow us
to relax these restrictions in order to produce the other 3 combinations. When the original query either does not
have phrases or the boolean operator, it can still be relaxed to the free text query.

Before any query is processed by the Vector Space Model (VSM) evaluation class Eval, it is parsed into a list where
each item is either a single term or a list of terms, which represents a phrase. The terms are also normalised with
case folding and stemming. The dictionary which includes the document frequencies and pointers to
the postings lists of each term in the postings file is read into memory. The document properties dictionary
which maps docIDs to the document vector lengths for normalisation is also read into memory.

The simplest search is done on free text queries without phrases or boolean operators (-phrase, -boolean). For such a
query, no intersection of posting lists is required. The postings lists for each term in the query is retrieved and
passed to the Eval class for evaluation according to the VSM. For queries with biword or triword phrases,
the postings list and term frequency of the phrase have to be retrieved using the algorithm described in PostionalMerge.
This merge returns all the documents in which the phrase occurs by merging the positional postings lists of the
individual terms that make up the phrase. The term frequency of the phrase in each document is found, and the length of
the postings list also represents the document frequency. The term and its document frequency is thus added to the
dictionary.

Where there are phrase queries, single words, biword, and triword phrases are evaluated as separate query vectors.
This is done because the assumption of independence between terms within the same vector might not hold if
phrasal and single terms are included within the same query vector. Furthermore, evaluating them as separate vectors
allows us to avoid recomputing a normalisation factor i.e. the document vector length whenever there is a phrase query.
Instead, the document properties files maps each document to the vector length for single words, biwords and triwords,
which can be used to normalise each vector. Therefore, each of the three query vectors (where there are single word,
biwords and triwords) are evaluated separated using the VSM, and the final cosine scores for each document are then
combined into a combined dictionary mapping documents to cosine scores before retrieving the most highly weighted
documents.

In other words, for any document, the final cosine score is calculated as:
a*(score from single term query vector) + b*(score from biword query vector) + c*(score from triword query vector).
The weights a, b and c can in principle be tuned through experimental findings. However, due to lack of data we have
decided to assign an equal weight for a, b and c.

If the query is a boolean query with the operator "AND", the posting lists for each term are reduced such that they
contain only documents that are shared between all postings lists. To do this, the merge algorithm in BooleanMerge
is used (see below). After the reduced postings lists are found, evaluation proceeds as in a non-boolean query using
the VSM evaluation. This is ensure that even though a strict intersection of all terms is enforced, the documents
can still be ranked.

### Vector Space Model evaluation

The VSM evaluation follows the lnc.ltc ranking scheme, such that we compute tf-idf for the query, but only log(tf)
for the documents. To evaluate each query, a list of (term, term frequency) tuples is created from the query.
Terms which are not found in the dictionary are ignored. This list of tuples is then converted into a truncated
query vector. Each component of the vector is multiplied by the idf of the term.

As in HW3, terms which do not appear in the query vector can be ignored since their tf-idf is 0 and have no effect
on the final cosine score, and only the documents that appear in at least one of the postings lists of the
query terms have to be considered. Thus, we iterate through each postings list of the query terms to obtain the
relevant components of each document vector. The term frequency in each posting is used to compute (1+log(tf)) directly,
which is multiplied with the already computed tf-idf score in the query vector and added directly to the cosine score
for that document.

The cosine scores are stored in dictionary mapping documents to cosine scores, which are then normalised using the
precomputed document vector lengths stored in the normalisation file. The query vector is not normalised since
normalisation has the same effect on the final cosine score of when comparing the query against each document.
Finally the scores are negated and a minheap is used to find the top documents.

## Merging Algorithms
### BooleanMerge

Since only "AND" operators were allowed, only the intersection algorithm involved in Boolean search was relavant.
The intersection of n postings lists was optimised by first sorting the lists based on the size of the list such
that the longest lists were merged first. Dynamically generated skip pointers were also used to speed up the
intersection.

### PositionalMerge

For identifying phrases, as positional indexing was done, each posting in the posting list was in the form
[docID, term frequency, position list]. In other to identify the documents with a biword phrase, the postings lists of
each term was merged by docID as in a conventional intersection algorithm used for merging postings lists in Boolean
search. Within the merge algorithm, when a docID which occurs in both postings lists is identified, an inner
merge algorithm is called on the position list for those two postings. Given two position lists such as [1,3,4,5] and
[4,5,6,7], the starting position of the phrase will be identified from the merge, such that [3,4,5] is returned.
The merging algorithm was optimised using dynamically generated skip pointers based on the size of the lists.
A similar approach is used to identify documents with triword phrases of the form "A B C". The posting list for
the phrase "A B" is first found, followed by "B C", and the two postings lists are then merged together.

## Query expansion
### Relaxing AND and phrasal queries


### Relevance Feedback and Rocchio Algorithm


### WordNet/Thesaurus Query Expansion



## Experimental Results

F2 results for documents appended in the following order:
1. positive list 2. -boolean, -phrase 3. +boolean +phrase 4. +phrase -boolean

Q1 Average F2: 0.0108201093105916
Q2 Average F2: 0.362745098039216
Q3 Average F2: 0.0112925624835047
Q4 Average F2: 0.496296296296296
Q5 Average F2: 0.103200491131526
Q6 Average F2: 0.30050505050505
Mean Average F2: 0.214143268

This is close to the baseline tf-idf.

F2 results for documents appended in the following order:
1. positive list 2. +boolean, +phrase 3. -boolean, -phrase 4. +phrase -boolean
5. Wordnet expansion 6. Rocchio expansion

Q1 Average F2: 0.0318471337579618
Q2 Average F2: 0.276839007986549
Q3 Average F2: 0.00854730742939909
Q4 Average F2: 0.516624579124579
Q5 Average F2: 0.103200491131526
Q6 Average F2: 0.172659817351598
Mean Average F2: 0.184953056130269

This performed worse than the baseline tf-idf.


== Files included with this submission ==

### need to regenerate class diagram

# data_helper.py - Manage the direct file reading and writing
# index.py - The driver file for indexing
# index-helper.py - The helper file for indexing, includes helper methods and data structures
# search.py - The driver file for search and query processing.
# search_helper.py - The helper file for search, query parsing and evaluation.
# PositionalMerge.py - The helper file for merging of posting and postional lists for identifying phrase queries.
# IntersectMerge.py - The helper file for merging of postings lists in Boolean queries.
# Eval.py - Evaluation class for computing cosine scores based on Vector Space Model (VSM).
# query_expander.py - ###

== Statement of individual work ==

[X] I, A0172868M, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions. 

[X] I, A0164816Y, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions. 

[X] I, A0168355W, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions. 

[X] I, A0171426J, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions. 

== References ==

Original source for data storage comparison, but it was overturned by our own investigations.
https://www.benfrederickson.com/dont-pickle-your-data/

Parallel Processing of Panda DataFrames
https://www.tjansson.dk/2018/04/parallel-processing-pandas-dataframes/

Date Processing
https://stackabuse.com/converting-strings-to-datetime-in-python/