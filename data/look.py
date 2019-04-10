"""
Simple python script to take a look at a document in the csv
"""
import pandas as pd
from pprint import pprint

print("What document id do you want to see")
file_no = input().strip()
print("Please wait")

filepath = "dataset.csv"
df = pd.read_csv(filepath, na_filter=False,
                    parse_dates=['date_posted'], index_col=False)


row = df[df["document_id"] == int(file_no)].iloc[0]
print(row["document_id"])
print('\r\n'.join([x for x in row["content"].splitlines() if x.strip()]))
