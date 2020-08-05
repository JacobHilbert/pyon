import timeit
import datetime
from statistics import mean, stdev
from math import log10, floor
from decimal import Decimal
import pyon,cson,yaml,json

# take a list, return its mean ± sample std in a correct format
# correct format means accurate decimal representation up to the order of magnitude of the std
def round_to(x,a):
	return round(x/a)*a
def mean_std(l:list):
	l = [*map(Decimal,l)]
	m = mean(l)
	std = stdev(l)
	exponent = Decimal(floor(log10(std)))
	std = round_to(std,10**exponent)
	m = round_to(m,10**exponent)
	return f"[{m},{std}]"
	
	
class Benchmark:
	obj = pyon.load("default.pyon")
	
	def pyon_load():
		return pyon.load("./dumped/pyon.pyon")
	def pyon_dump():
		return pyon.dumps(Benchmark.obj)
	def cson_load():
		with open("./dumped/cson.cson") as file:
			return cson.loads(file.read())
	def cson_dump():
		return cson.dumps(Benchmark.obj,indent=4)
	def yaml_load():
		with open("./dumped/yaml.yml") as yaml_file:
			return yaml.safe_load(yaml_file)
	def yaml_dump():
		return yaml.dump(Benchmark.obj,default_flow_style=False,sort_keys=False)
	def json_load():
		with open("./dumped/json.json") as file:
			return json.loads(file.read())
	def json_dump():
		return json.dumps(Benchmark.obj,indent=4)


def load_times(lang:str,number:int=100,per_loop:int=10) -> str:
	return [timeit.timeit(getattr(Benchmark,lang+"_load"),number=per_loop) for _ in range(number)]
def dump_times(lang:str,number:int=100,per_loop:int=10) -> str:
	return [timeit.timeit(getattr(Benchmark,lang+"_dump"),number=per_loop) for _ in range(number)]

if __name__ == "__main__":
	# dump all versions

	with open("./dumped/pyon.pyon","w") as file:
		file.write(Benchmark.pyon_dump())
	with open("./dumped/cson.cson","w") as file:
		file.write(Benchmark.cson_dump())
	with open("./dumped/json.json","w") as file:
		file.write(Benchmark.json_dump())
	with open("./dumped/yaml.yml","w") as file:
		file.write(Benchmark.yaml_dump())

	# Benchmark!
	
	n = 100
	pl = 50
	
	print(f"""# Default PyON benchmark at {str(datetime.datetime.now(datetime.timezone.utc))}
# Made with {n} loop, {pl} repetitions per loop. Divide by {pl} to obtain single run duration.
# Data is in [mean,std] format, in seconds

""")
	print("pyon:")
	print(f"\tload: {mean_std(load_times('pyon',n,pl))}")
	Benchmark.obj = Benchmark.pyon_load()
	print(f"\tdump: {mean_std(dump_times('pyon',n,pl))}\n")
	
	print("cson:")
	print(f"\tload: {mean_std(load_times('cson',n,pl))}")
	Benchmark.obj = Benchmark.cson_load()
	print(f"\tdump: {mean_std(dump_times('cson',n,pl))}\n")
	
	print("json:")
	print(f"\tload: {mean_std(load_times('json',n,pl))}")
	Benchmark.obj = Benchmark.json_load()
	print(f"\tdump: {mean_std(dump_times('json',n,pl))}\n")
	
	print("yaml:")
	print(f"\tload: {mean_std(load_times('yaml',n,pl))}")
	Benchmark.obj = Benchmark.yaml_load()
	print(f"\tdump: {mean_std(dump_times('yaml',n,pl))}\n")

