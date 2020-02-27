import json
import logging
import os
from collections import OrderedDict
from operator import itemgetter
import sys

#logger to make debugging easier
log = logging.getLogger(__name__)
#set last arg to "INFO", "WARNING", "ERROR", "DEBUG", or whatever
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))

#loads a set of primes saved in a json file, primes.txt
def load_primes():

    primes = {}
 
    #loading the json into an ordered dict. It has the structure of JSON while still being ordered
    #this was important for having a flexible file format and still having quick searches
    log.info("Opening primes.txt file")
    try:
        f = open('primes.txt')
        raw_json = json.load(f)
        primes = OrderedDict(sorted(raw_json.items(), key=itemgetter(1)))
    except:
        log.warning("Error loading prime file. Primes will be overwritten. Continue? (y/n)")
        if raw_input() != 'y':
            exit
        primes = OrderedDict([('2', 2), ('3', 3), ('5', 5)])
    return primes
                            
#returns the max value of the primes. NOTE: Not efficient; loads primes file.
def get_max():
    log.info("Checking get_max of primes")
    primes = load_primes()
    max_val = max(primes.values())
    return max_val

#adds primes between the current max prime and the threshold value to the file primes.txt
def find_primes(threshold):
    threshold = int(threshold)
    
    primes = load_primes()
    
    f = open('primes.txt', 'w+')
    
    log.info("Calculating primes up to {}".format(threshold))
    cur_val = max(primes.values())
    log.info("Starting at value: {}".format(cur_val))
    while cur_val < threshold:
        cur_val += 2
        is_prime = True
        for index, prime in primes.items():
            if cur_val%prime == 0:
                is_prime = False
                break
        if is_prime:
            primes[str(cur_val)] = cur_val
        
    json.dump(primes, f)

def factorize(x, primes):
    soln = OrderedDict([('1',{'value': 1, 'count': 1})])
    bound = (x/2)+1
    orig_val = x
    
    for index, prime in primes.items():
        if prime > bound:
            break
        while x%prime == 0:
            try:
                soln[str(prime)]['count'] += 1
            except:
                soln[str(prime)] = {'value': prime, 'count': 1}
            x = x/prime
    if len(soln) == 1:
        soln[str(orig_val)] = {'value': orig_val, 'count': 1}
    return soln

#this file takes an argument for the threshold
#i.e. python NumTheory.py 10000
if len(sys.argv) > 1:
    find_primes(sys.argv[1])
