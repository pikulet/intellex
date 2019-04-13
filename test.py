import pandas as pd
import sys
from data_helper import *

filepath = "../dataset/dataset.csv"
df = read_csv(filepath)

def get_doc(docID):
    rows = df[df["document_id"] == int(docID)].iterrows()
    text = ""
    for idx, row in rows:
        line = '\r\n'.join([x for x in row.loc["content"].splitlines() if x.strip()])
        text += line
    text = text.split()
    return text

word_lists = []

for docID in [2223478,2225511,6072585,2914577,2888569,6666862,2914577,2725285,2238071,2762199]:
    words = set(get_doc(docID))
    word_lists.append(words)

print(word_lists[0].intersection(word_lists[1], word_lists[2], word_lists[3], word_lists[4]))

