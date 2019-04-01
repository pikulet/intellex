import msgpack
import json
import ujson
import pickle
import timeit
import numpy as np

num_tests = 100

obj = np.random.random((40, 40))

command = 'pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)'
setup = 'from __main__ import pickle, obj'
result = timeit.timeit(command, setup=setup, number=num_tests)
print("Pickle:   %f seconds" % result)


command = 'pickle.dumps(obj, protocol=4)'
setup = 'from __main__ import pickle, obj'
result = timeit.timeit(command, setup=setup, number=num_tests)
print("Pickle highest:   %f seconds" % result)

command = 'json.dumps(obj.tolist())'
setup = 'from __main__ import json, obj'
result = timeit.timeit(command, setup=setup, number=num_tests)
print("json:   %f seconds" % result)

command = 'ujson.dumps(obj.tolist())'
setup = 'from __main__ import ujson, obj'
result = timeit.timeit(command, setup=setup, number=num_tests)
print("ujson:   %f seconds" % result)

command = 'msgpack.packb(obj.tolist())'
setup = 'from __main__ import msgpack, obj'
result = timeit.timeit(command, setup=setup, number=num_tests)
print("msgpack:   %f seconds" % result)