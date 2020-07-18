import pyon

# General autoconsistency test
test = pyon.load("test.pyon")
print(pyon.loads(pyon.dumps(test)) == test)