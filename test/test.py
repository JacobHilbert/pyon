import pyon
import os

# General autoconsistency test
print("Doctests on __ingredients.py:\n")
import doctest
from pyon import __ingredients
doctest.testmod(__ingredients,verbose=True)

test = pyon.load("test.pyon")
if str(pyon.loads(pyon.dumps(test))) == str(test):
	print("\nConsistency test passed: loads and dumps behave as inverse functions, at least in string representation of the dict.")
	print("Cannot compare directly due to the non trivial comparation of nan float values","\n\n")
else:
	print("Consistency test failed")
	print("test dict was:")
	print(f"\t{test}")
	print("but loads(dumps(test)) was:")
	print(f"\t{pyon.loads(pyon.dumps(test))}")
	
