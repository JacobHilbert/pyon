import pyon
import os

# General autoconsistency test
test = pyon.load("test.pyon")
if pyon.loads(pyon.dumps(test)) == test:
	print("Consistency test passed: loads and dumps behave as inverse functions")
else:
	print("Consistency test failed")
	print("test dict was:")
	print(f"\t{test}")
	print("but loads(dumps(test)) was:")
	print(f"\t{pyon.loads(pyon.dumps(test))}")
	
print("Doctests on __ingredients.py:\n")

import doctest
from pyon import __ingredients
doctest.testmod(__ingredients,verbose=True)