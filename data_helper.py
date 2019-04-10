'''
All of the data access calls are stored here. 

Requisite: 
python 3.4 or above

Backing Protocol:
Pickle
Pandas
'''
import pickle
import pandas as pd

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
                     parse_dates=['date_posted'], index_col=False, encoding="utf-8")
    df = df.sort_values("document_id", ascending=True)
    return df

########################## SPEED TESTING ##########################

# The file writing and reading was done using different modules for comparison

# ujson with gzip
# def store_data(filepath, data):
#     start = time.time()
#     with gzip.GzipFile(filepath, 'w') as f:
#         f.write(ujson.dumps(data).encode('utf-8'))
#     end = time.time()
#     print(end - start)

# def load_data(filepath):
#     start = time.time()
#     with gzip.GzipFile(filepath, 'r') as f:
#         data = ujson.loads(f.read().decode('utf-8'))
#     end = time.time()
#     print(end - start)
#     return data

# ujson
# def store_data(filepath, data):
#     start = time.time()
#     with open(filepath, 'w') as f:
#         ujson.dump(data, f)
#     end = time.time()
#     print(end - start)

# def load_data(filepath):
#     start = time.time()
#     with open(filepath, 'r') as f:
#         data = ujson.load(f)
#     end = time.time()
#     print(end - start)
#     return data

# json
# def store_data(filepath, data):
#     start = time.time()
#     with open(filepath, 'w') as f:
#         json.dump(data, f)
#     end = time.time()
#     print(end - start)

# def load_data(filepath):
#     start = time.time()
#     with open(filepath, 'r') as f:
#         data = json.load(f)
#     end = time.time()
#     print(end - start)
#     return data

# pickle proto 4
# def store_data(filepath, data):
#     start = time.time()
#     with open(filepath, 'wb') as f:
#         pickle.dump(data, f,  protocol=4)
#     end = time.time()
#     print(end - start)

# def load_data(filepath):
#     start = time.time()
#     with open(filepath, 'rb') as f:
#         data = pickle.load(f)
#     end = time.time()
#     print(end - start)
#     return data

# pickle proto 3
# def store_data(filepath, data):
#     start = time.time()
#     with open(filepath, 'wb') as f:
#         pickle.dump(data, f)
#     end = time.time()
#     print(end - start)

# def load_data(filepath):
#     start = time.time()
#     with open(filepath, 'rb') as f:
#         data = pickle.load(f)
#     end = time.time()
#     print(end - start)
#     return data
