import pandas as pd
import timeit
import csv
import gc
import sys
import time

num_tests = 1

filename = "../data/dataset.csv"


def open_with_python_csv():
    csv.field_size_limit(100000000)
    data = []
    with open(filename, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            data.append(row)
    return data


def open_with_pandas_read_csv():
    df = pd.read_csv(filename)
    data = df.values
    return data


def open_with_pandas_special_read_csv():
    df = pd.read_csv(filename, engine='c', na_filter=False, parse_dates=['date_posted'] )
    data = df.values
    return data


def simple_timer(func, repeats=3):
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

simple_timer(open_with_python_csv)
simple_timer(open_with_pandas_read_csv)
simple_timer(open_with_pandas_special_read_csv)