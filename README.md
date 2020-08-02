# pyon
An attempt of python object notation. Highly inspired on CSON, but with a more more permissive yet definite grammar.

## Installation

On this folder:
```
pip install . -e
```

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

- [ ] Write tests for

	- [ ] implementation functions

	- [x] API

- [ ] Correct the indentation on multiline strings (!)

- [ ] Allow `nan`, `inf` and `-inf`, the IEEE 754 special floats.

	* Problem: the safe `ast.literal_eval` cannot handle those.

- [ ] Provide line-by-line syntax errors

- [ ] Benchmarking against CSON and JSON

