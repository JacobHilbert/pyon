import ast
import re
import base64

pattern = {
	# 1
	"string"            : r"(?<!\\)('''|\"\"\"|\"|')([\S\s]*?)(?<!\\)\1",
	"comment"           : r"#[\S\s]*?\n",
	"free_key"          : r"(\t*)([^' \n,\{]+)(?= *:)",
	"comma_worth"       : r"([^:,])$",
	"indent_level"      : r"^(\t*)([^\n]*?)$",
	"dedent_no_comma"   : r"\)(?!,)",
	"complex"           : r"\((\d+(?:\+|\-)\d+j)\)",
}

CSON = {
	"true"  : "True",
	"false" : "False",
	"null"  : "None",
}

# 1


def quote_escape(s:str) -> str:
	'''Escapes the quotes on `s`. " -> \"
	The converse of this operation is quote_activate'''
	return re.sub(r"(?<!\\)(\'|\")",r"\\\1",s) # pending, pattern unscaped_quote

def quote_activate(s:str) -> str:
	'''Un-escapes the quotes on `s`. \" -> "
	The converse of this operation is quote_escape'''
	return re.sub(r"\\(\'|\")",r"\1",s)

def special_escape(s:str) -> str:
	return s.replace("\n","\\n").replace("\t","\\t")

def special_activate(s:str) -> str:
	return s.replace("\\n","\n").replace("\\t","\t")

def string_index_replace(text:str, i:int, rep:str) -> str:
	'''Returns a copy of `text` with the character at position `i` replaced by `rep`.'''
	tmp = list(text)
	tmp[i] = rep
	return "".join(tmp)

def url_encode(text:str) -> str:
	return base64.urlsafe_b64encode(text.encode()).decode()

def url_decode(text:str) -> str:
	return base64.urlsafe_b64decode(text.encode()).decode()

def literal_string_encode(match:re.match) -> str:
	'''url_encode, but as a response for re.sub.
	Intended to be used with pattern['string'], as it expects \\1 to be the quote kind and \\2 its contents.
	It always returns a single-quoted string'''
	return f"'{url_encode(match.group(2))}'"

def literal_string_decode(match:re.match) -> str:
	'''url_decode, but as a response for re.sub.
	Intended to be used with pattern['string'], as it expects \\1 to be the quote kind and \\2 its contents.
	It produces single-quote strings when possible, but when the string contains a \n character, is converted to triple quotes.
	It scapes all quotes and activates all escape sequences.'''
	string = special_activate(quote_escape(url_decode(match.group(2))))
	kind = "'''" if "\n" in string else match.group(1)
	return kind+string+kind

def is_raw_key(text:str) -> bool:
	"Is `text` parseable as a hashable type?"
	try:
		hash(ast.literal_eval(text))
		return True
	except (ValueError,TypeError): # from ast.literal_eval, from hash
		return False

def free_key_quote(match:re.match) -> str:
	'''Response to re.sub, returns a quoted free-key if \\2 is a valid python identifier'''
	level = match.group(1)
	key = match.group(2)
	if is_raw_key(key):
		return level+key
	elif key.isidentifier():
		return f"{level}'{url_encode(key)}'"

def which_structure(text:str) -> (list,dict,False):
	'''Determines wheter text can be parsed as a dict or a list
	`text` should not have the outermost brackets.
	Returns False if the parser fails.
	'''
	try:
		return type(ast.literal_eval(f"[{text}]"))
	except (SyntaxError, ValueError):
		try:
			return type(ast.literal_eval(f"{{{text}}}"))
		except (SyntaxError, ValueError):
			return False

def innermost_structure_index(text:str) -> (int,int):
	'''
	Returns the starting and ending index of `text` that corresponds to the deepest nested matching parenthesis.
	Usage:
		struct = innermost_structure_index(text)
		text[slice(*struct)] # contents
		text[struct[0]-1] # left parenthesis
		text[struct[1]] # right parenthesis
	'''
	try:
		end_index = text.index(")")
		begin_reversed_index = list(reversed(text[:end_index])).index("(")
		return (end_index - begin_reversed_index, end_index)
	except ValueError:
		return False