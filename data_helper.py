'''
All of the data access calls involving writing and
reading from the file system are stored here.

Universal methods should be stored here too.

Requisite:
python 3.4 or above

Backing Protocol:
Pickle
Pandas
'''

import pickle
import pandas as pd
import math
from datetime import datetime
from nltk import PorterStemmer

##################################################################
### UNIVERSAL METHODS
##################################################################

PORTER_STEMMER = PorterStemmer()
### Normalise a term by case folding and porter stemming
def normalise_term(t):
    return PORTER_STEMMER.stem(t.lower())

### Parse the date format from csv file
def dateparse(x):
    return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")

### Get log tf, given the normal tf
def log_tf(x):
    return 1 + math.log(x, 10)

##################################################################
### DATA ACCESS METHODS
##################################################################

def store_data(filepath, data):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f,  protocol=pickle.HIGHEST_PROTOCOL)

def load_data(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data


def store_data_with_handler(file, data):
    pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)


def load_data_with_handler(file, offset):
    file.seek(offset)
    data = pickle.load(file)
    return data


def read_csv(filepath):
    df = pd.read_csv(filepath, na_filter=False,
                     parse_dates=['date_posted'], index_col=False, date_parser=dateparse, encoding="utf-8")
    df = df.sort_values("document_id", ascending=True)
    return df
