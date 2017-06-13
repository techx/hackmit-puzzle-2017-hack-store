import hashlib
import time
import base64
import re

PASSWORD_REGEX = re.compile('^[A-Za-z0-9]{6,12}$')

def good_pass(password):
    return PASSWORD_REGEX.search(password) != None

# deterministic password
# given gh and username
def gen_password(secret, gh, username):
    s = ''.join([secret, gh, username]).encode('utf8')
    res = base64.b64encode(hashlib.sha256(s).digest()).decode('utf8').replace('=', 'E').replace('+', 'P').replace('/', 'S')[:10]
    # there's a real cool attack you could do here, woulnd't really help you though ;)
    return res

def slow_compare(a, b, delay):
    correct = len(a) == len(b)
    for i in range(min(map(len, [a, b]))):
        if a[i] != b[i]:
            return False
        time.sleep(delay)
    return correct
