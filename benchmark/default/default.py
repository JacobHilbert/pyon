import timeit
import pyon,cson,yaml,json


def test_pyon():
	pyon.load("pyon.pyon")
def test_cson():
	with open("cson.cson") as file:
		test_cson = cson.loads(file.read())
def test_yaml():
	with open('yaml.yml') as yaml_file:
		yaml.safe_load(yaml_file)
def test_json():
	with open("json.json") as file:
		test_json = json.loads(file.read())

print(f"pyon: {timeit.timeit(test_pyon,number=1000):4.2f}s")
print(f"cson: {timeit.timeit(test_cson,number=1000):4.2f}s")
print(f"json: {timeit.timeit(test_json,number=1000):4.2f}s")
print(f"yaml: {timeit.timeit(test_yaml,number=1000):4.2f}s")


