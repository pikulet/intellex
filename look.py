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
filepath = "data/dataset.csv"
df = read_csv(filepath)

row = df[df["document_id"] == int(file_no)].iloc[0]
print(row["document_id"])
line = '\r\n'.join([x for x in row["content"].splitlines() if x.strip()])
sys.stdout.buffer.write(line.encode('utf-8'))