from CardanoToolsSymPy import *
from Primes import *
'''

print("Factoring")
print(factorize(52, primes))
print(factorize(920, primes))
print(factorize(493, primes))
print(factorize(83, primes))
'''
#sol_checker(84, 84, 1000)

brute_force_solve_range_multi(18000000, limit=110000000, splits=10)
