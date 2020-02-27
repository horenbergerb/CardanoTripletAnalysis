# CardanoTripletAnalysis

Contains multiple files for experimenting with Cardano triplets.

Primes.py contains code for generating, saving, and loading primes in primes.txt. It also contains code for factoring numbers
Primes.txt contains primes in a JSON format.

CardanoTools.py contains a bunch of hacky code for counting cardano triplets. Currently not rigged to save results, although this would greatly speed up future runs.
I'm waiting to save results to a file until I've verified them and preferably implemented the a+b+c<L limit.

CardanoTest.py actually runs the tools from CardanoTools.


TO DO:
Create the a+b+c<L limit code.
       NOTE: I've been thinking a=n but this is NOT true. Fix this in math.
       Can we do this efficiently? counting solutions is currently so elegant, but this bound seems to impose a lot more computation on it.

Compare with Zach's code. Are we counting the same values?

Add useful debug stuff. I got lazy halfway through writing it.

Make Cardano tools more modular.

Add visualizations. Could be of solutions or of Cardano eq in general. Get creative. Probably use a separate file for visualizations.

Create explicit solution computation and storage. Seems overkill but may provide geometric insight