rem Please ensure that you have at least 8 GB of free ram
py -3.6 index.py -i "data/dataset.csv" -d "dictionary.txt" -p "postings.txt"
py -3.6 search.py -d "dictionary.txt" -p "postings.txt" -o "output.txt" -q "queries.txt"