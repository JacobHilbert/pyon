import re
import ast

from .__ingredients import *

def load(filename:str, encoding='utf-8', indent_mode="\t"):
	with open(filename, encoding=encoding, mode="r") as file:
		return loads(file.read())

def dump(obj:dict, filename:str, encoding='utf-8', indent_mode="\t", file_mode="w"):
	with open(filename, encoding=encoding, mode=file_mode) as file:
		return file.write(dumps(obj))

def loads(text:str, indent_mode="\t") -> dict:
	result = text
	# 1.1
	result = re.sub(pattern["string"],literal_string_encode,result)
	# 1.2
	result = re.sub(pattern["comment"],"\n",result)
	# 1.3
	for k,v in CSON.items():
		result = result.replace(k,v)
	# 1.4
	result = re.sub(pattern["free_key"],free_key_quote, result)
	# 1.5
	result = result.replace(indent_mode,"\t")
	# 1.6
	result = re.sub(r"\t+\n","\n",result)
	# 1.7
	result = result.replace(" ","")
	# 2.1
	level = 0
	result_lines = ["{"]
	matches = [m for m in re.findall(pattern["indent_level"],result,flags=re.MULTILINE) if m[1]]
	for m in matches:
		this_level = len(m[0])
		level_diff = this_level - level
		this_line = re.sub(pattern["comma_worth"],r"\1,",m[1])
		if   level_diff > 0:
			this_line = "«"* level_diff + this_line
		elif level_diff < 0:
			this_line = "»"*-level_diff + this_line
		result_lines.append(this_line)
		level = this_level
	# 2.2
	result_lines.append("»"*level)
	result_lines.append("}")
	result = "".join(result_lines)
	# 2.3
	result = re.sub(pattern["dedent_no_comma"],"»,",result)
	# 3
	open_struct = {list:"[",dict:"{"}
	close_struct = {list:"]",dict:"}"}
	while (i := innermost_structure_index(result)):
		kind = which_structure(re.sub(pattern["string"],literal_string_decode,result[slice(*i)]))
		result = string_index_replace(result,i[0]-1,open_struct[kind])
		result = string_index_replace(result,i[1],close_struct[kind])
	# 4
	result = re.sub(pattern["string"],literal_string_decode,result)
	result = special_escape(result)
	return tuned_literal_eval(result)

def dumps(obj:dict, indent_mode="\t") -> str:
	if not isinstance(obj,dict):
		raise TypeError("PyON dump is only intended for dict, but "+type(obj).__name__+" passed.")
	else:
		# 1.1
		result = repr(obj)
		# 1.2
		result = re.sub(pattern["string"],literal_string_encode,result)
		# 1.3
		result = re.sub(pattern["complex"],r"\1",result)
		# 1.4
		# must replace by the url-enconded string, later decoding will assume this
		result = result.replace("nan","float('bmFu')").replace("inf","float('aW5m')")
		# 1.5
		result = result.replace(" ","")
		# 1.6 
		result = result.replace("[]","LIST").replace("{}","DICT")
		# 1.7 
		result = re.sub(r"\{|\["," « ",result)
		result = re.sub(r"\}|\]"," » ",result)
		# 1.8
		result = result.replace("LIST","[]").replace("DICT","{}")
		# 2 restructure
		result_lines = []
		level = 0
		last = ""
		for this in [s for s in re.split(" |,",result) if s][1:-1]:
			if this == "«":
				if last == "»":
					result_lines.append(level*"\t"+",") # put a comma between same-level structures
				level += 1
			elif this == "»":
				level -= 1
			else:
				result_lines.append(level*"\t"+this)
			last = this
		result = "\n".join(result_lines)
		# 3
		result = re.sub(pattern["string"],literal_string_decode,result)
		return result