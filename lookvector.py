import pandas as pd
import sys
from pprint import pprint
from data_helper import *
from QueryExpansion import *

file_no = ""
if len(sys.argv) > 1 :
    file_no = sys.argv[1].strip()
else:
    print("What document id do you want to see")
    file_no = input().strip()

d = get_centroid_vector([int(file_no)])
from operator import itemgetter
for k, v in sorted(d.items(), key=itemgetter(1)):
    print (k, v)