from Primes import load_primes, factorize, get_max
import logging
import sys
import os
from collections import OrderedDict
from operator import itemgetter
from math import sqrt
import itertools
import copy

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
    max_val = 1
    #load the file if not provided
    if cardano == None:
        cardano = load_cardano()
    if bool(cardano):
        #getting the largest n value in the file. converts to int since dict indexes are strings
        max_val = max(cardano, key=int)
    return max_val

#gross solution for factoring (n^2)*(8n-3). each n value as well as (8n-3) and calculates soln set
#interesting to note: if you've factored some n, you could just tack on primes and have the factorizations for those too.
#i.e. instead of iterating n from 1 to some limit, you could construct n from primes, and then you'd only have to factor (8n-3)
#also note b=n is always a solution and seems to be the lowest value of a+b+c
def brute_force_n_factors(n, primes, prefactored_n = None):

    n_square_factors = None
    #we can re-use multiples of previously factored n values
    #particularly, we re-use n*2
    if prefactored_n != None:
        n_square_factors = prefactored_n
    else:
        n_square_factors = factorize(n, primes)

    n_double_factors = copy.deepcopy(n_square_factors)
    try:
        n_double_factors['2']['count'] += 1
    except:
        n_double_factors['2'] = {'value': 2, 'count': 1}
    
    #our first term is n^2 so double the factors
    for key in n_square_factors:
        n_square_factors[key]['count'] = n_square_factors[key]['count']*2

    #now factor the 2nd term, (8n-3)
    term_2_factors = factorize(((8*n)-3), primes)
    
    #combining factors
    total_factors = n_square_factors
    #combining is currently not graceful
    for key in term_2_factors.keys():
        try:
            total_factors[key]['count'] += term_2_factors[key]['count']
        except:
            total_factors[key] = {'value': int(key), 'count': term_2_factors[key]['count']}

    #finally, set the count on '1' back to '1'
    total_factors['1']['count'] = 1

    if n%10000 == 0:
        print("n: {}".format(n))#, (n*n)*((8*n)-3)))
    #log.debug("n: {} (n^2)(8*n-3): {}".format(n, (n*n)*((8*n)-3)))
    #log.debug("yielded: {}".format(total_factors))
    
    return total_factors, n_double_factors, term_2_factors

#depricated. counting will not be useful until we can count solutions which satisfy the limit a+b+c<N and we have not solved this.
'''
#counts the solutions of (b^2)(c) given a factorization of the left-hand side
def count_solutions_for_n(n, cur_factors):
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
'''
#solves the values of b,c in (b^2)(c) given a factorization of the left-hand side
def solve_solutions_for_n(n, cur_factors, limit = None):    
    #first we count the number of options for b
    #always starts at 1 since b=1 is valid
    b_factors = [[1]]
    b_solutions = []
    for cur_factor in cur_factors.keys():
        if cur_factors[cur_factor]['count'] > 1:
            #put all factors that could be in b in a list
            #dividing by 2 since b is squared
            prime_powers = [1]
            for power in range(1, (cur_factors[cur_factor]['count']//2)+1):
                prime_powers.append(cur_factors[cur_factor]['value']**power)
            if prime_powers != [1]:
                b_factors.append(prime_powers)
                
    factor_combos = list(itertools.product(*b_factors))

    #actual values of b
    b_solutions = [reduce((lambda x, y: x*y), z) for z in factor_combos]

    #checking limit conditions
    if limit != None:
        left_side = (n*n)*((8*n)-3)
        x = 0
        while x < len(b_solutions):
            if ((3*n-1) + b_solutions[x] + (left_side/(b_solutions[x]*b_solutions[x]))) > limit:
                #print("Soln over limit:")
                #print(b_solutions[x])
                b_solutions.pop(x)
            else:
                x+=1
                
    #since knowing n and b implies c, we don't need to count anything else!
    return b_solutions

#verfies a solution. good for debugging
def sol_checker(n, b, limit):
    a = 3*n-1
    c = ((n*n)*(8*n-3))/(b*b)
    left_hand = (n*n)*(8*n-3)
    print("a = {}, b = {}, c = {}".format(a,b,c))
    print("b*b*c = (n*n)*(8*n-3): {}".format(bool(left_hand == b*b*c)))
    print("a+b+c < {}: {}".format(limit, bool(a+b+c < limit)))
    

#depricated since counting is difficult to account for a+b+c < N limit
'''
#count cardano solutions in a very bland way, using brue_force_n_factors
def brute_force_count_range(max_n, primes, save_results = False, limit=None):
    cardano = load_cardano()
    start_val = get_max_n(cardano = cardano)
    total_sols = 0
    
    log.info("Counting cardano solutions from {} to {}".format(start_val, max_n))
    #calculating new n values (x is n)
    for x in range(start_val, max_n):
        #factoring the left-hand side of the eq
        cur_factors = brute_force_n_factors(x, primes)
        #counting possible solutions of (b^2)(c) using the factorization
        sol_count = count_solutions_for_n(x, cur_factors, limit=limit)
        total_sols += sol_count

        #print(sol_count)
        #add_cardano_soln(x, sol_count, cur_factors)
'''

#count cardano solutions in a very bland way, using brute_force_n_factors
def brute_force_solve_range(max_n, primes, limit=None ,save_results = False):
    #cardano = load_cardano()
    #start_val = get_max_n(cardano = cardano)
    start_val = 1
    
    total_sols = 0

    zero_count = 0
    
    log.info("Counting cardano solutions from {} to {}".format(start_val, max_n))
    #calculating new n values (x is n)
    max_prime = get_max(primes)
    #we hold on to the factors of (8n-3) and reuse them 
    term_2_factors = []
    #for every n we factor, we hold on to the factorization of 2n and reuse it
    prev_2n_factors = []
    for x in range(start_val, max_n):
        
        #factoring the left-hand side of the eq
        #if we've already factored this n as a previous (8n-3), reuse it
        short_cut = None
        if x%2 == 0:
            short_cut = prev_2n_factors.pop(0)
            #print("n value: {} hacked factors: {}".format(x, short_cut))
        elif x%8 == 5:
            short_cut = term_2_factors.pop(0)
        cur_factors, new_2n_factors, new_2nd_term_factors = brute_force_n_factors(x, primes, prefactored_n = short_cut)
        prev_2n_factors.append(new_2n_factors)
        term_2_factors.append(new_2nd_term_factors)
        
        #getting all possible solutions of (b^2)(c) using the factorization
        #print(cur_factors)
        sols = solve_solutions_for_n(x, cur_factors, limit=limit)
        #print(sols)
        if len(sols) == 0:
            zero_count += 1
        else:
            total_sols += len(sols)
            zero_count = 0
        '''
        if len(sols) == 0:
            log.info("Hit boundary; no solutions at n={} and limit={}".format(x, limit))
            break
        '''
        if ((8*x)-3)/2 > max_prime:
            log.error("Desired Cardano values larger than available primes :( Terminating...")
            break
    print("Total solutions: {}".format(total_sols))
    print("Consecutive Zeros: {}".format(zero_count))

    
