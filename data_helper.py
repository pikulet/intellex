import ujson
import codecs
import gzip
import time
import json

def store_data(filepath, data): 
    with gzip.GzipFile(filepath, 'w') as f:
        f.write(ujson.dumps(data).encode('utf-8'))

def load_data(filepath):
    with gzip.GzipFile(filepath, 'r') as f:
        data = ujson.loads(f.read().decode('utf-8'))
    return data

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

# slower ujson
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

# # slower json
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