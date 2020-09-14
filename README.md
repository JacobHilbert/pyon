# pyon
An attempt of python object notation. Highly inspired on CSON, but with a more more permissive yet definite grammar.

## Installation

On this folder:
```
pip install .
```

## What is allowed

This is a package intended to serialize python `dict` objects, so the main object shoul be a dictionary.

The values of this main `dict` could be (almost) any of the bsic data types of python:
* antoher `dict`
* a `list`
* Any unicode string (`"` and `'`), including multine (`'''` and `"""`)
* Any number, including:
	* `float`, and floating point special values `float('nan')`, `float('inf')` and `-float('inf')`
	* Any arbitrary size sinteger
	* Complex numbers, in the format `{re}+{im}j`
* boolean values `True` and `False`
* `None`

The only exception is the `set` class. I see no point on serializing sets; just use lists.

Dict keys in python must be _hashable_, which narrows the options to:
* strings
* numbers
	* `float` is not recommended as a dict key, due to its natural problem with the `==` operator.
* booleans
* `None`

### Examples

#### simple dict

```python
# Python onle line
{"a":1, "b":2, "c":{"a":1, "b":2}}

# Python multi line
{
	"a":1,
	"b":2,
	"c": {
		"a":1,
		"b":2,
	}
}

# pyon
a: 1
b: 2
c: 
	a: 1
	b: 2
```
(You can ommit the string quotes on the key if the key is a valid varaible name, i.e. has only letters, numbers and `_`)

#### list

```python
# Python one line
{"my list":[1,2,3,[4,5,6]]}

# Python multiline
{
	"my list": [
		1,
		2,
		3,
		[
			4,
			5,
			6,
		]
	]
}

# pyon
"my list":
	1
	2
	3
		4
		5
		6
```

#### list of dicts

```python
# Python one line
{"list of dicts":[{"a":1,"b":2},{"a":10,"b":20}]}

# Python multi line
{
	"list of dicts": [
		{
			"a":1,
			"b":2
		},{
			"a":10,
			"b":20
		}
	]
}

# pyon
"list of dicts" :
		a:1
		b:2
	, 
		a:10
		b:20
```
That comma must be one indentation level less that the objects it separates.



## API

Similar to the `json` stdlib package:

* `pyon.load(filename)` to load a file. `pyon.loads(string)` to parse a string

* `pyon.dump(d,filename)` to dump a dictionary `d` into a file. `pyon.dumps(d)` to dump a dictionary into a string



## Specification

I will use a [modified BNF grammar](https://docs.python.org/3/reference/introduction.html#notation) like the python reference's one, but with some additions. Real quick:

* `token`
* `"literal characters"`
* `token ::= definition`
* `(token grouping)`
* `token+` one or more of token
* `tiken*` zero or more of token
* `a|b|c` options (only one)
* `{indented section}` a newline with one more indentation level than the one before
* `<externally defined token>` a python defined token.

The full grammar is:
```
file ::= struct*
struct ::= key ":" ( value | {struct}+ | multi_list+ ) <NEWLINE>
key ::= <identifier> | hashable
value ::= <list> | <dict> | hashable
hashable ::= <str> | <int> | <float> | <complex> | <bool> | <None>
multi_list ::= ( {value} | {multi_list} ) | ( {struct}+ {","} )
```

Note: this definition of hashable is not the full extent of python's hashable classes.

## Implementation details

The implementation, in a formant with some semblance of a cooking recipe, can be found as a `README.md` in the pyon folder.

## TO DO

- [ ] Check the grammar

- [x] Write tests for

	- [x] implementation functions

	- [x] API

- [ ] Correct the indentation on multiline strings (!)

- [x] Allow `nan`, `inf` and `-inf`, the IEEE 754 special floats.

	* Problem: the safe `ast.literal_eval` cannot handle those.
	
	* Solution: write my own `literal_eval` that allows that safely.

- [ ] Provide line-by-line syntax errors

- [ ] Benchmarking against CSON and JSON

