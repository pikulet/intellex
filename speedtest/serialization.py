import msgpack
import json
import ujson
import pickle
import timeit
import numpy as np
import gc
import sys
import time


obj = np.random.random((200, 200))

def open_with_pickle():
    pickle.dumps(obj, protocol=4)


def open_with_pickle_highest():
    pickle.dumps(obj, protocol=4)


def open_with_json():
    json.dumps(obj.tolist())


def open_with_ujson():
    ujson.dumps(obj.tolist())


def open_with_msgpack():
    msgpack.packb(obj.tolist())

def simple_timer(func, repeats=100):
    gc.disable()
    total = 0.
    for i in range(0, repeats):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        total += end - start
        gc.collect()

    print("{} {}".format(func, total / repeats))

    gc.enable()
    return

simple_timer(open_with_pickle)
simple_timer(open_with_pickle_highest)
simple_timer(open_with_json)
simple_timer(open_with_ujson)
simple_timer(open_with_msgpack)

