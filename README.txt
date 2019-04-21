This is the README file for the submission of
A0172868M-A0171426J-A0168355W-A0164816Y

e0202438@u.nus.edu
e0200996@u.nus.edu
e0176788@u.nus.edu
e0148858@u.nus.edu

@@@ write the final decision

== Python Version ==

We're using Python Version <3.6> for this assignment.

== General Notes about this assignment ==

# Analysis of the Corpus

A short corpus analysis is done to understand the data we are working with:
https://notebooks.azure.com/jason-soh/projects/homework4/html/index.ipynb
There are a total of 17137 documents in the corpus, and 31 types of courts in the court field.
We found that all the fields were populated.

We identified some cases of duplicate document IDs, which does not make sense in the context of document
retrieval (see duplicate_docs fuke). We analysed these duplicate entries and found that these entries would have the
title and content being repeated, and the only field changed would be the metadata on the court.

Such occurrences make sense in real life, since legal cases can be transferred between courts depending on their
severity. To treat the case of a duplicate document, we simply update the court and keep the case with
the highest priority. While this may compromise on accuracy, it is almost impossible to determine if the
case went from a high-priority court to a low-priority court or vice versa. We believe that using the
highest priority reflects the importance of a case better. We also update the total number of documents
(subtract 1), which is used in the calculation on idf on query terms.

We also found some Chinese documents from HK High Court and HK Court of First Instance (duplicated
data). More specifically, this was in document 2044863. We did not add any special processing methods
because the case is isolated and it is unlikely that the user wants to look something up from the document.
There are also other unicode characters that are not recognised. These can be easily resolved with utf-8 encoding.

# System Architecture

We divided our system into three main components: Indexing, Helper Modules, Searching.

The indexing modules are used for the indexing algorithm.
The helper modules are used for BOTH indexing and searching. (File reading and writing, shared term normalisation methods, shared constants)
The searching modules work with document ranking and query expansion.

# Indexing

We first tokenise the documents using the nltk tokenisers with stemming and case folding as in previous homeworks.
Our aim is to model the baseline tf-idf method as closely as possible. The increased features would mostly come
from the searching stage, where we perform query expansion.

## Parallelising NLTK tokenisation
When running our initial indexing on the Tembusu cluster, we found that the indexing time was infeasible
to work with. Given a lot of changes we wanted to make in terms of storing biwords, which document
properties, we wanted to speed up the indexing time. We timed the different parts of the indexing and
found the NLTK tokenisation to take a significant portion of the time.

In HW3, the program would perform nltk(doc1), then nltk(doc2), then nltk(doc3). Given that the documents
are fairly independent, we do not actually have to wait for nltk(doc1) to complete before starting on
nltk(doc2). Instead of doing the tokenisation sequentially, we realised we could read in all the data,
pass all the documents to be tokenised in parallel, then process the tokenised data sequentially.

(done in parallel): doc1, doc2, doc3... --> nltk(doc1), nltk(doc2), nltk(doc3)...
(sequential): process(tokenised_doc1), process(tokenised_doc2), process(tokenised_doc3)...

We still have to process the documents sequentially because we wanted the posting lists to be sorted by
docID for quicker merging for AND queries. If we processed the docIDs non-sequentially, we would have to
do a sort operation on all the final posting lists, which is time-consuming.

## Storing entire document vectors

We processed the document content body and title body separately, so we have two sets of a dictionary and
posting list, one for the content+title body and one for the title body. We explain our choice of including
the title metadata in ### METADATA - TITLE below.

In the processing, we store the dictionary and posting list data as in HW3. However, we also store the actual document
uniword vector. This vector maps the count of every term in the document.

For example, doc1 { "egg" : 1, "cat" : 3, "the" : 4 }

We subsequently apply log-tf on the counts. Previously in HW3, we would just store the length of this vector as the
document length. Now,  we also store the entire vector because we need the vector for relevance feedback
(see section on Rocchio Algorithm).

While storing the entire vector takes up a lot of space (370MB), we chose to make this tradeoff. The
alternative was to run through the entire posting list to reconstruct the document vector during searching
time. To reconstruct doc1 above, we run through the posting lists of ALL terms, and record which terms contain
doc1. Considering that this process has to be repeated for all the documents involved in the relevance
feedback, it would take up a lot of time in searching, compromising on the search efficiency.Of course, the next
alternative is to forego Rocchio expansion altogether, but we still kept it for experimentation purposes.

## Processing document metadata

DOCUMENT METADATA - TITLE
When considering how to process the document metadata, we saw that the title was mostly a repetition of
the first line of the content. That is, there is no additional data in the title. This means that the
title was meant to separate parts of the content that were deemed more important. We thus experimented with
giving a higher weight to the title field later on.

However, it is likely that the title is too short and contains too many numbers and case references. When
we experimented with weighing the title and content as two separate zones of the document, we did not get
good results, often performing below the baseline.

As such, we decided to approach the baseline as closely as possible. We hypothesised that the baseline model
merged both the title and content together, so we did just that. We had one set of processed data for TITLE
only, one set of processed data for TITLE + CONTENT.

DOCUMENT METADATA - COURT
Without good prior knowledge on court orders and their nuances, we assigned courts a priority between 1 to 3,
with 1 being the high priority courts. We used the court ordering provided.

DOCUMENT METADATA - DATE POSTED
When processing the date posted, we interpreted that data as being a metadata of the document. That is,
the date posted has no actual content that the user will look up. Users are only likely to search for the
hearing or incident dates. We used the date posted then, as an indicator of how recent the case was. More
specifically, we recorded the seconds from indexing time as a proxy. Nevertheless, the date posted is
unlikely to be an important distinguishing factor. After some experiments, we omitted this result from the
document ranking, though we still kept the data.

## Storing biword and triword information

Later on in the searching, we want to add phrasal biwords and triwords (marked in quotation marks " ")
to the VSM as an additional dimension. These dimensions can be weighted differently, since having a
phrase would be more meaningful than just containing a uniword.

When iterating through the documents, we also collect information on the biword and triword counts, to
produce the biword and triword vectors. Unfortunately, it would be unfeasible to store all the data for
searching. Given a corpus size of 700MB, the uniword posting list and dictionary already takes up about
641MB of space. Storing the biword and triword information as separate indices would not be good in terms
of space usage. As such, we took to using positional indexing to store data on biwords and triwords. That
is, to find the term frequency of "fertility treatment" in document 1, we run a positional merge on the
posting list of "fertiltiy" and "treatment" for document 1.

However, we need information on vector length for the VSM scores. It is not efficient to calculate the
document length at search time for the same reason why we store the entire document vector for the Rocchio
expansion. As such, we collect information on the biword and triword vectors of a document at indexing
time. Every document has a count for all its biword and triword terms. We use the log-tf on the terms,
similar to the uniword vector, then saved the length of the biword and triword vectors.

At searching time, we retrieve term frequencies of phrases using positional merge, and lookup on the
document lengths for the biword and triword vectors. For the queries, we count the document frequencies of
phrases by compiling the results of the positional merge (combining posting list of "fertility" and
"treatment"). The idf is then calculated using this data.

We found this method to be the best tradeoff between space and time. The operations which are inefficient
and take up little space (document length for biword and triword vectors) are done at indexing time and
stored. The operations which can be done quickly, and take up too much space when stored (term frequencies
and document frequencies) are done at searching time.

## Summary of index content

As mentioned above, we have two set of index contents, one for the TITLE ONLY and one for TITLE + CONTENT.
We re-specify this in the "files included" section.

dictionary_title.txt - dictionary of terms that appear in all the titles
postings_title.txt - posting lists for terms that appear in all the titles

dictionary.txt - dictionary of terms that appear in all the title + content combined
postings.txt - posting lists for terms that appear in all the title + content combined

We also keep track of document properties and metadata, such as the document length and court.

document_properties.txt - dictionary mapping docID to document properties

postings_vector.txt - storing all the actual document vectors.
The byte offset needed for unpickling is stored as a document property.

A summary of the document properties we kept track of:
- CONTENT_LENGTH: vector length for document vector from TITLE + CONTENT
- TITLE_LENGTH: vector length for document vector from TITLE only
- COURT_PRIORITY: priority of document court from 1 (highest priority) to 3 (lowest)
- DATE_POSTED: an indicator of how recent the document was posted (in seconds from indexing time)
- VECTOR_OFFSET: the byte offset for pickle to load the document content + title vector from postings_vector.txt
- BIGRAM_CONTENT_LENGTH: length of document TITLE + CONTENT biword index, for normalisation of triword terms
- TRIGRAM_CONTENT_LENGTH: length of document TITLE + CONTENT triword index, for normalisation of triword terms
- BIGRAM_TITLE_LENGTH: length of document TITLE only biword index, for normalisation of triword terms
- TRIGRAM_TITLE_LENGTH: length of document TITLE only triword index, for normalisation of triword terms

# Helper Modules

We have three helper modules that are consistently used across indexing and searching.

## data_helper.py

The data helper contains shared methods, and direct file reading and writing.
Shared methods includes NLTK tokenisation methods, since we want to apply consistent tokenisation for both the document and query.

The direct file reading and writing is handled by pickle, but we abstract everything here so we could experiment with different
serialisation modules (JSON, XML). We wanted to experiment with this aspect because our initial searching was very slow and inefficient.
We did online research (see references) on serialisation methods, and tested them out. In the end, our results still directed us back to pickle.

## properties_helper.py

The properties helper module manages document properties. We store the constants needed to access the specific document properties here.
Having this module was useful in our experimentation, because we could add more document metadata easily. Document properties have no 
actual relevance to document retrieval, and they mostly help with the relative ranking of the retrieved documents, and for relevance feedback.

For example:
(1) lengths are used in normalisation of scores
(2) court and data metadata can be weighed in the scores
(3) document vectors are used for relevance feedback

## constants.py

(1) Test files
This file contains the test files we were working with. For example, we only index the first 100 entries for most of the testing phase for
indexing. We can run this indexing locally, and the indexing of the full 17 000 entries on Tembusu.

(2) Intermediate files
As shown above, we have a lot of intermediate files (that are not dictionary.txt and postings.txt). These file names are stored here to be
written to at indexing time and read from at searching time.

(3) Searching Parameters
To facilitate our experimentation, we tried a lot of settings for the search. These settings are encapsulated here, for example we can
set weights and ranking orders.

# Searching

At the top level of searching, query expansion is first done to the original query string to produce
multiple versions of the same query (see section on query expansion). Every query can one of the following four types:

1. +phrase, + boolean: e.g. "fertility treatment" AND damages
2. +phrase, -boolean: e.g. "fertility treatment" damages
3. -phrase, +boolean: e.g. fertility AND treatment AND damages
4. -phrase, -boolean: e.g. fertility treatment damages (basic free text query without phrases or boolean operator)

For an original query string with both phrases and the "AND" boolean operator, query expansion can allow
us to relax these restrictions in order to produce the other 3 combinations. When the original query
either does not have phrases or the boolean operator, it can still be relaxed to the free text query.
For a maximally complex query of type 1 (including boolean operator and phrases), the orders of search between
these four types of queries can be permuted and experimented with to determine the importance of preserving
the additional information of phrases and boolean operators.

### Final decision here !!!!!!!!!!!

Before any query is processed by the Vector Space Model (VSM) evaluation class Eval, it is parsed into a
list where each item is either a single term or a list of terms, which represents a phrase. The terms are
also normalised with case folding and stemming. The dictionary which includes the document frequencies and
pointers to the postings lists of each term in the postings file is read into memory. The document
properties dictionary which maps docIDs to the document vector lengths for normalisation is also read into
memory.

The simplest search is done on free text queries without phrases or boolean operators (-phrase, -boolean).
For such a query, no intersection of posting lists is required. The postings lists for each term in the
query is retrieved and passed to the Eval class for evaluation according to the VSM. For queries with
biword or triword phrases, the postings list and term frequency of the phrase have to be retrieved using
the algorithm described in PostionalMerge. This merge returns all the documents in which the phrase occurs
by merging the positional postings lists of the individual terms that make up the phrase. The term
frequency of the phrase in each document is found, and the length of the postings list also represents the
document frequency. The term and its document frequency is thus added to the dictionary.

Where there are phrase queries, single words, biword, and triword phrases are evaluated as separate query
vectors. This is done because the assumption of independence between terms within the same vector might
not hold if phrasal and single terms are included within the same query vector. Furthermore, evaluating
them as separate vectors allows us to avoid recomputing a normalisation factor i.e. the document vector
length whenever there is a phrase query. Instead, the document properties files maps each document to the
vector length for single words, biwords and triwords, which can be used to normalise each vector.
Therefore, each of the three query vectors (where there are single word, biwords and triwords) are
evaluated separated using the VSM, and the final cosine scores for each document are then combined into a
combined dictionary mapping documents to cosine scores before retrieving the most highly weighted
documents.

In other words, for any document, the final cosine score is calculated as:
a*(score from single term query vector) + b*(score from biword query vector) + c*(score from triword query
vector). The weights a, b and c can in principle be tuned through experimental findings. However, due to
lack of data we have decided to assign an equal weight for a, b and c.

If the query is a boolean query with the operator "AND", the posting lists for each term are reduced such
that they contain only documents that are shared between all postings lists. To do this, the merge
algorithm in BooleanMerge is used (see below). After the reduced postings lists are found, evaluation
proceeds as in a non-boolean query using the VSM evaluation. This is ensure that even though a strict
intersection of all terms is enforced, the documents can still be ranked. The merging essentially retrieves
a list of documents we want to consider. The VSM then tells us the relative scores of these documents
that have been retrieved.

In addition, given that title and content were indexed separately, it is possible to run the same query twice
to derive the cosine scores from searching the title and content fields, which are then combined using a linearly
weighted function of the form:
a*(score from title search) + b*(score from content search)
This functionality was implemented, but due to lack of training data, it was not possible to learn the appropriate
weights that should be assigned to each field. One experiment was done on assigning an equal weight, which performed
worse than a simple tf-idf baseline and was hence omitted.

## Vector Space Model evaluation

The VSM evaluation follows the lnc.ltc ranking scheme, such that we compute tf-idf for the query, but only
log(tf) for the documents. To evaluate each query, a list of (term, term frequency) tuples is created from
the query. Terms which are not found in the dictionary are ignored. This list of tuples is then converted
into a truncated query vector. Each component of the vector is multiplied by the idf of the term.

As in HW3, terms which do not appear in the query vector can be ignored since their tf-idf is 0 and have
no effect on the final cosine score, and only the documents that appear in at least one of the postings
lists of the query terms have to be considered. Thus, we iterate through each postings list of the query
terms to obtain the relevant components of each document vector. The term frequency in each posting is
used to compute (1+log(tf)) directly, which is multiplied with the already computed tf-idf score in the
query vector and added directly to the cosine score for that document.

The cosine scores are stored in dictionary mapping documents to cosine scores, which are then normalised
using the precomputed document vector lengths stored in the normalisation file. The query vector is not
normalised since normalisation has the same effect on the final cosine score of when comparing the query
against each document. Finally the scores are negated and a minheap is used to find the top documents.

## Merging Algorithms
### BooleanMerge

Since only "AND" operators were allowed, only the intersection algorithm involved in Boolean search was
relavant. The intersection of n postings lists was optimised by first sorting the lists based on the size
of the list such that the longest lists were merged first. Dynamically generated skip pointers were also
used to speed up the intersection.

### PositionalMerge

For identifying phrases, as positional indexing was done, each posting in the posting list was in the form
[docID, term frequency, position list]. In other to identify the documents with a biword phrase, the
postings lists of each term was merged by docID as in a conventional intersection algorithm used for
merging postings lists in Boolean search. Within the merge algorithm, when a docID which occurs in both
postings lists is identified, an inner merge algorithm is called on the position list for those two
postings. Given two position lists such as [1,3,4,5] and [4,5,6,7], the starting position of the phrase
will be identified from the merge, such that [3,4,5] is returned. The merging algorithm was optimised
using dynamically generated skip pointers based on the size of the lists. A similar approach is used to
identify documents with triword phrases of the form "A B C". The posting list for the phrase "A B" is
first found, followed by "B C", and the two postings lists are then merged together.

## Query expansion

### Relaxing boolean and phrasal queries

The first stage of query expansion, as explained above, involves relaxing the restrictions placed on the query from
phrases and boolean operators. Since the terms in the user queries may not be the exact terms desired, we need to
relax the AND portion of the query, so that even if the term given is not correct, the results for other parts of the
query can still be returned. To achieve a baseline tf-idf framework, all boolean operators and phrase markers were
stripped from the query string.

### WordNet/Thesaurus Query Expansion

The NLTK WordNet was used as a thesaurus to implement query expansion. In particular, the synonyms of the terms
were found using the synset feature of WordNet. Additionally, we also experimented with using hypernyms and
hyponyms to return related words, however, because too many of such words were returned, we decided to stick with
synonyms. The additional synonyms retrieved were appended onto the free text version of the original query to create
a longer free text query. Due to time constraints we were unable to implement a potential improvement, which involves
ensuring for a boolean query that the synonyms were intersected. For example, a query 'quiet AND phone call' could be
expanded to '(quiet OR silent) AND (phone call OR telephone call)'.

### Relevance Feedback and Rocchio Algorithm

For relevance feedback based on the Rocchio Algorithm, our system makes use of the top 1000 returned documents
from the basic search which are assumed to be relevant, on top of the list of documents identified as relevant
in the original query file. The document IDs are then used to retrieve precomputed and stored document vectors in
the document properties file, which are then combined to give the centroid vector of the relevant documents. This is
done such that there is no need to traverse the postings file to build the document vector for each relevant document,
which would be extremely expensive.

An additional optimisation involves storing the vectors as sparse vectors using a dictionary mapping terms to the tf
values. This is necessary since the vectors would include many 0 terms if the dimension of the vector was the size of
the entire dictionary. Furthermore, even after computing the centroid vector, there will still remain many non-zero
dimensions in the centroid. In order to improve on efficiency, there is a need to remove some of the non-zero terms.
To do this, each component was multiplied with idf in order to reduce the value of more common and hence less
useful terms. The top 50 terms were chosen for the final centroid vector.

The new centroid vector can then be added to the original query vector to derive a new query vector used for VSM
retrieval. For simplicity, the original query vector is made to be a free text query such that boolean operators
are removed and phrases are converted to single word terms. The additional documents found from relevance feedback
are appended after the already returned documents.

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

....

== Files included with this submission ==

# diagram.png - visualisation of our system architecture
# duplicate_docs - duplicate document IDs from corpus analysis

# constants.py
# data_helper.py - Manage the direct file reading and writing
# properties_helper.py 

# index.py - The driver file for indexing
# Dictionary.py
# PostingList.py

# search.py - The driver file for search and query processing.
# search_helper.py - The helper file for search, query parsing and evaluation.
# PositionalMerge.py - The helper file for merging of posting and postional lists for identifying phrase queries.
# BooleanMerge.py - The helper file for merging of postings lists in Boolean queries.
# Eval.py - Evaluation class for computing cosine scores based on Vector Space Model (VSM).
# QueryExpansion.py - File including code for query expansion, WordNet/thesaurus expansion, and relevance feedback.


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
