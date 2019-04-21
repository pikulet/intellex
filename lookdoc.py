"""
NOT PART OF THE HW

Simple python script to take a look at a document in the csv

"""

import pandas as pd
import sys
from data_helper import *

file_no = ""
if len(sys.argv) > 1 :
    file_no = sys.argv[1].strip()
else:
    print("What document id do you want to see")
    file_no = input().strip()

print("Please wait...")
filepath = "../dataset/dataset.csv"
df = read_csv(filepath)

rows = df[df["document_id"] == int(file_no)].iterrows()
for idx, row in rows:
    print(row.loc["document_id"])
    print("\n")
    print(row.loc["title"])
    print("\n")
    print(row.loc["date_posted"])
    print("\n")
    print(row.loc["court"])
    print("\n")
    line = '\r\n'.join([x for x in row.loc["content"].splitlines() if x.strip()])
    sys.stdout.buffer.write(line.encode('utf-8'))
    print("\n\n")