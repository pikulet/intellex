This is the README file for the submission of
A0172868M, A0171426J, A0168355W

e0202438@u.nus.edu
e0200996@u.nus.edu
e0176788@u.nus.edu

== Python Version ==

I'm using Python Version <3.6> for this assignment.

== General Notes about this assignment ==

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


== Files included with this submission ==

# data_helper.py - Manage the direct file reading and writing
# index.py - The driver file for indexing
# index-helper.py - The helper file for indexing, includes helper methods and data structures
# search.py - The driver file for query processing
# search_helper.py - The helper file for query parsing and evaluation
# PositionalMerge.py - 
# IntersectMerge.py
# Eval.py - Evaluator file for query
# query_expander.py 

== Statement of individual work ==

[X] I, A01......, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions. 

[X] I, A01......, certify that I have followed the CS 3245 Information
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

Original source for data storage comparsion, but it was overturned by our own investigations. 
https://www.benfrederickson.com/dont-pickle-your-data/

Parallel Processing of Panda DataFrames
https://www.tjansson.dk/2018/04/parallel-processing-pandas-dataframes/

Date Processing
https://stackabuse.com/converting-strings-to-datetime-in-python/