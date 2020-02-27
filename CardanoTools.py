from Primes import load_primes, factorize
import logging
import sys
import os
from collections import OrderedDict
from operator import itemgetter
from math import sqrt

#logger to make debugging easier
log = logging.getLogger(__name__)
#set last arg to "INFO", "WARNING", "ERROR", "DEBUG", or whatever
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))

#we are attacking positive integer solutions to ((n+1)^2)*(8n+5)=(b^2)*c
#any n value may yield many solutions of b and c
#the solutions are determined by the factorization of the left side

#the left-hand equation in question can be considered as f(n) = ((n+1)^2)*(8n+5)
#plugging in f(n-1) yields ((n)^2)*(8n-3) which is slightly easier to work with

#so if we construct n from the set of primes, then find the factorization of (8n-3),
#we have the factors of the left side, thus we must consider
#all distinct combinations of the factors satisfying (b^2)*c
#i.e. say the left side factors to 2*2*5*5*13
#then b could be 1, 2, 5, or 2*5, and in each case c is the remaining factors

#OPTIMIZE FACTORIZATION OF (8n-3)

#loads solutions saved in a json file, cardano.txt
def load_cardano():

    cardano = {}
 
    #loading the json into an ordered dict. It has the structure of JSON while still being ordered
    #this was important for having a flexible file format and still having quick searches
    #format:
    #indexed by n values
    #{n1: {count:  , factors: []}, n2: {count: , factors: []}, n3...}
    log.info("Opening cardano.txt file")
    try:
        f = open('cardano.txt')
        raw_json = json.load(f)
        cardano = OrderedDict(sorted(raw_json.items(), key=itemgetter(1)))
    except:
        log.warning("Error loading cardano file. Cardano will be overwritten. Continue? (y/n)")
        if raw_input() != 'y':
            exit
        cardano = OrderedDict()
    return cardano

#adds a new solution to the cardano file
def add_cardano_soln(n, count, factors, cardano = None):
    #load the file if not provided
    if cardano == None:
        cardano = load_cardano()

    #never update old solutions
    if str(n) in cardano:
        return
    
    cardano[str(n)] = {'count': count, 'factors': factors}
        
#returns the max n value currently solved. Pass it the Cardano dict to speed up process
def get_max_n(cardano = None):
    log.info("Checking get_max of cardano")
    max_val = 2
    #load the file if not provided
    if cardano == None:
        cardano = load_cardano()
    if bool(cardano):
        #getting the largest n value in the file. converts to int since dict indexes are strings
        max_val = max(cardano, key=int)
    return max_val

#gross solution for factoring (n^2)*(8n-3). each n value as well as (8n-3) and calculates soln set
def brute_force_n_factors(n, primes):
    #first factor n
    n_square_factors = factorize(n, primes)
    #our first term is n^2 so double the factors
    for key in n_square_factors:
        n_square_factors[key]['count'] = n_square_factors[key]['count']*2

    #now factor the 2nd term, (8n-3)
    term_2_factors = factorize(((8*n)-3), primes)
    
    #combining factors
    total_factors = n_square_factors.copy()
    #combining is currently not graceful
    for key in term_2_factors.keys():
        try:
            total_factors[key]['count'] += term_2_factors[key]['count']
        except:
            total_factors[key] = {'value': int(key), 'count': 1}

    #finally, set the count on '1' back to '1'
    total_factors['1']['count'] = 1
    
    log.debug("n: {} (n^2)(8*n-3): {}".format(n, (n*n)*((8*n)-3)))
    #log.debug("yielded: {}".format(total_factors))

    return total_factors

#counts the solutions of (b^2)(c) given a factorization of the left-hand side
def count_solutions_for_n(n, cur_factors, limit=None):
    #getting upper and lower bounds on solutions
    #lower bound approx when b=c=sqrt((n^2)(8n-3))
    lower_bound = n + 2*sqrt((n*n)*((8*n)-3))
    #upper bound when b=1 or c=1, approximately
    upper_bound = n + (n*n)*((8*n)-3) + 1

    #log.info("n: {}, upper soln sum: {}, lower soln sum: {}".format(n, upper_bound, lower_bound))
    
    #first we count the number of options for b
    #always starts at 1 since b=1 is valid
    b_options = 1
    for cur_factor in cur_factors.keys():
        if cur_factors[cur_factor]['count'] > 1:
            #counts the ways this factor could be in b
            #dividing by 2 since b is squared
            factor_options = cur_factors[cur_factor]['count']//2
            #multiply b_options by our options for each prime in the factorization
            b_options *= factor_options
            
    #since knowing n and b implies c, we don't need to count anything else!
    return b_options

#count cardano solutions in a very bland way, using brue_force_n_factors
def brute_force_count_range(max_n, primes, save_results = False):
    cardano = load_cardano()
    start_val = get_max_n(cardano = cardano)
    total_sols = 0
    
    log.info("Counting cardano solutions from {} to {}".format(start_val, max_n))
    #calculating new n values (x is n)
    for x in range(start_val, max_n):
        #factoring the left-hand side of the eq
        cur_factors = brute_force_n_factors(x, primes)
        #counting possible solutions of (b^2)(c) using the factorization
        sol_count = count_solutions_for_n(x, cur_factors, limit=110000000)
        total_sols += sol_count

        print(sol_count)
        #add_cardano_soln(x, sol_count, cur_factors)
    print("Total solutions from n={} to n={}: {}".format(start_val, max_n, total_sols))
    print("Maximum (n^2)(8*n-3): {}".format((max_n*max_n)*((8*max_n)-3)))
