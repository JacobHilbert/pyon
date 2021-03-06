import ast
import re
import base64

pattern = {
	"string"            : r"(?<!\\)('''|\"\"\"|\"|')([\S\s]*?)(?<!\\)\1",
	"comment"           : r"#[\S\s]*?\n",
	"free_key"          : r"(\t*)([^' \n,\{]+)(?= *:)",
	"comma_worth"       : r"([^:,])$",
	"indent_level"      : r"^(\t*)([^\n]*?)$",
	"dedent_no_comma"   : r"\»(?!,)",
	"complex"           : r"\((\d+(?:\+|\-)\d+j)\)",
}

CSON = {
	"true"  : "True",
	"false" : "False",
	"null"  : "None",
}

def tuned_literal_eval(node_or_string):
	"""
	Safely evaluate an expression node or a string containing a Python
	expression.  The string or node provided may only consist of the following
	Python literal structures: strings, bytes, ints, floats, complexes, tuples, 
	lists, dicts, sets, booleans, and None.
	
	This is a tuned version of the python stdlib ast literal_eval, modified to
	accept float("nan") and float("inf") special values, possibly signed.
	
	>>> tuned_literal_eval("float('nan')")
	nan
	>>> tuned_literal_eval("float('inf')")
	inf
	>>> tuned_literal_eval("-float('inf')")
	-inf
	"""
	if isinstance(node_or_string, str):
		node_or_string = ast.parse(node_or_string, mode='eval')
	if isinstance(node_or_string, ast.Expression):
		node_or_string = node_or_string.body
	def _raise_malformed_node(node):
		raise ValueError(f'malformed node or string: {node!r}')
	def _convert_num(node):
		if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and
			  node.func.id == 'float' and len(node.args)==1 and node.args[0].value in ["nan","inf"]):
			return float(_convert(node.args[0]))
		elif not isinstance(node, ast.Constant) or type(node.value) not in (int, float, complex):
			_raise_malformed_node(node)
		return node.value
	def _convert_signed_num(node):
		if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
			operand = _convert_num(node.operand)
			if isinstance(node.op, ast.UAdd):
				return + operand
			else:
				return - operand
		return _convert_num(node)
	def _convert(node):
		if isinstance(node, ast.Constant):
			return node.value
		elif isinstance(node, ast.Tuple):
			return tuple(map(_convert, node.elts))
		elif isinstance(node, ast.List):
			return list(map(_convert, node.elts))
		elif isinstance(node, ast.Set):
			return set(map(_convert, node.elts))
		elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and
			  node.func.id == 'set' and node.args == node.keywords == []):
			return set()
		elif isinstance(node, ast.Dict):
			if len(node.keys) != len(node.values):
				_raise_malformed_node(node)
			return dict(zip(map(_convert, node.keys),
							map(_convert, node.values)))
		elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
			left = _convert_signed_num(node.left)
			right = _convert_num(node.right)
			if isinstance(left, (int, float)) and isinstance(right, complex):
				if isinstance(node.op, ast.Add):
					return left + right
				else:
					return left - right
		return _convert_signed_num(node)
	return _convert(node_or_string)

def quote_escape(s:str) -> str:
	'''
	Escapes the quotes on `s`.
	The converse of this operation is quote_activate
	'''
	return re.sub(r"(?<!\\)(\'|\")",r"\\\1",s)

def quote_activate(s:str) -> str:
	'''
	Un-escapes the quotes on `s`. 
	The converse of this operation is quote_escape
	'''
	return re.sub(r"\\(\'|\")",r"\1",s)

def special_escape(s:str) -> str:
	'''
	Escapes tab and newlines
	The converse of this operation is special_activate
	'''
	return s.replace("\n","\\n").replace("\t","\\t")

def special_activate(s:str) -> str:
	'''
	Un-escapes tab and newlines
	The converse of this operation is special_escape
	'''
	return s.replace("\\n","\n").replace("\\t","\t")

def string_index_replace(text:str, i:int, rep:str) -> str:
	'''
	Returns a copy of `text` with the character at position `i` replaced by `rep`.
	
	>>> string_index_replace("abcd",2,"j")
	'abjd'
	'''
	tmp = list(text)
	tmp[i] = rep
	return "".join(tmp)

def url_encode(text:str) -> str:
	'''
	Encondes the text to make it url safe
	
	>>> url_encode("abcd")
	'YWJjZA=='
	'''
	return base64.urlsafe_b64encode(text.encode()).decode()

def url_decode(text:str) -> str:
	'''
	Decodes a string encoded by url_encode.
	
	>>> url_decode("YWJjZA==")
	'abcd'
	'''
	return base64.urlsafe_b64decode(text.encode()).decode()

def literal_string_encode(match:re.match) -> str:
	'''
	url_encode, but as a response for re.sub.
	Intended to be used with pattern['string'], as it expects \\1 to be the quote kind and \\2 its contents.
	It always returns a single-quoted string
	
	>>> import re
	>>> re.sub(r'("+)([\s\S]*)\\1',literal_string_encode,'asdasd"""asd\\nasd"""asdasd')
	"asdasd'YXNkCmFzZA=='asdasd"
	'''
	return f"'{url_encode(match.group(2))}'"

def literal_string_decode(match:re.match) -> str:
	"""
	url_decode, but as a response for re.sub.
	Intended to be used with pattern['string'], as it expects \\1 to be the quote kind and \\2 its contents.
	It produces single-quote strings when possible, but when the string contains a \n character, is converted to triple quotes.
	It scapes all quotes and activates all escape sequences.
	
	>>> import re
	>>> re.sub(r"(')([\s\S]*)\\1",literal_string_decode,"asdasd'YXNkCmFzZA=='asdasd")
	"asdasd'''asd\\nasd'''asdasd"
	"""
	string = special_activate(quote_escape(url_decode(match.group(2))))
	kind = "'''" if "\n" in string else match.group(1)
	return kind+string+kind

def is_raw_key(text:str) -> bool:
	'''
	Is `text` parseable as a hashable type?
	
	>>> is_raw_key("abcd")
	False
	>>> is_raw_key("False")
	True
	>>> is_raw_key("1e4")
	True
	'''
	try:
		hash(tuned_literal_eval(text))
		return True
	except (ValueError,TypeError): # from tuned_literal_eval, from hash
		return False

def free_key_quote(match:re.match) -> str:
	'''
	Response to re.sub, returns a quoted free-key if \\2 is a valid python identifier.
	\\1 is assumed to be the indentation level.
	String key is encoded.
	
	>>> import re
	>>> re.sub(r"(\\t*)([^' \\n,\{]+)(?= *:)",free_key_quote,"\\ta:4")
	"\\t'YQ==':4"
	>>> re.sub(r"(\\t*)([^' \\n,\{]+)(?= *:)",free_key_quote,"\\t'a':4")
	"\\t'a':4"
	'''
	level = match.group(1)
	key = match.group(2)
	if is_raw_key(key):
		return level+key
	elif key.isidentifier():
		return f"{level}'{url_encode(key)}'"

def which_structure(text:str) -> (list,dict,False):
	'''
	Determines wheter text can be parsed as a dict or a list
	`text` should not have the outermost brackets.
	Returns False if the parser fails.
	
	>>> which_structure("4:3")
	<class 'dict'>
	>>> which_structure("4,3")
	<class 'list'>
	>>> which_structure("while True: print(3)")
	False
	'''
	try:
		return type(tuned_literal_eval(f"[{text}]"))
	except (SyntaxError, ValueError):
		try:
			return type(tuned_literal_eval(f"{{{text}}}"))
		except (SyntaxError, ValueError):
			return False

def innermost_structure_index(text:str) -> (int,int):
	'''
	Returns the starting and ending index of `text` that corresponds to the deepest nested matching parenthesis.
	
	>>> t = "out «1st nest «2nd nest» 1st nest» out"
	>>> struct = innermost_structure_index(t)
	>>> struct
	(15, 23)
	>>> t[slice(*struct)] # contents
	'2nd nest'
	>>> t[struct[0]-1]
	'«'
	>>> t[struct[1]]
	'»'
	'''
	try:
		end_index = text.index("»")
		begin_reversed_index = list(reversed(text[:end_index])).index("«")
		return (end_index - begin_reversed_index, end_index)
	except ValueError:
		return False