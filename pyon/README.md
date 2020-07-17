# Recipes: PyON implementation

#### Equipment

From the standard library:

* `ast`
	* `literal_eval`
* `re`
	* `match`
	* `sub`
	* `split`
	* `findall`
	* `MULTILINE`
* `base64`
	* `urlsafe_b64decode`
	* `urlsafe_b64encode`

## Load a `dict` from a PyON string

### 1. Encoding

#### Ingredients

* `string` pattern: `(?<!\\)('''|\"\"\"|\"|')([\S\s]*?)(?<!\\)\1`
	* `\1`: quote style
	* `\2`: contents

* `literal_string_encode(match:re.match) -> str` and `literal_string_decode(match:re.match) -> str` functions. Given a match on the text, this functions return the appropiate replacement to encode or decode it.

* `comment` pattern: `#[\S\s]*?\n`

* `CSON -> PyON` bool and None mapping

* `free_key` pattern: `(\t*)([^' \n,]+)(?= *:)`. Don't worry about the quoting style.
	* `\1`: indentation level
	* `\2`: key

* `is_raw_key(text:str) -> bool` function.

* `free_key_quote(match:re.match) -> str` function to manage the replacement of free keys for quoted ones. Quoted key must be encripted.

* `INDENT_MODE` string. Tab, or amount of spaces that constitutes one tab.
	* `"\t"` by default
	* Cannot possibly be inferred.

We recommend organizing your patterns in a dictionary, to avoid unnecesary mess in the kitchen.

#### Procedure

1. Use `re.sub` with `literal_string_encode` to encode all explicit strings into url-safe bytes. This way all strings with be single quoted, and its content will be secure against global word replacements.

1. Use `re.sub` and the comments pattern to wipe'em out. This must be done after the encoding to avoid a massacre against strings with `#` characters.

1. Use the CSON mapping to correct things like `false` to `False` and `null` to `None`.

1. Quote the free keys

1. Replace `INDENT_MODE` with a single tab.

1. Blank only-indent lines. A recommendend way to do this is `\t+\n` -> `\n`

1. Delete all spaces.

### 2. Engraving

#### Ingredients

* `comma_worth` end of line pattern: `([^:,])$` __This is a multiline pattern__

* `indent_level` pattern: `^(\t*)([^\n]*?)$` __This is a multiline pattern__
	* `\1` : indentation
	* `\2` : line content

* `dedent_no_comma` pattern: `\)(?!,)`

#### Preparation

Indentation level is set to `0`.

There should be a list to hold the engraved lines. Its first element must be and `{`

#### Procedure


1. Loop through all the lines:

	* Ignore blank lines
	* Check if there is a match of `comma_worth`, and replace it by itself with a comma.
	* Obtain the indentation level and line content with the pattern `indent_level`.
	* Compare the indentation level of this line with the one before
		* If it's bigger, put as many `(` at the beginning of the line as de difference
		* If it's lower, put as many `)` at the beginning of the line as de difference

2. Add a line with as many `)` as the current indentation level, and a final `}`.

3. Put a comma on those closing `)` that have no commas, using the pattern `dedent_no_comma`.

### 3. Identify structures

#### Ingredients

* `wich_structure(line:str) -> {list,dict}` function, which examines a string and determines if it is a python list or a dictionary. It hopefully raises a descriptive error is `line` is not list neither dict. (not implemented)

* `string_replace_index(text:str,i:int,rep:str) -> str` function that returns a version of `text` with the `i`-th character replaced by `

* `innermost_structure_index(text:str) -> (int,int)` function, that searches for the deepest nest of `()` and returns the indices of the opening and close `()`

#### Preparation

Clean the string from `\n` and tabs.

#### Procedure

1. Get the most inner structure contents via slices and `innermost_structure_index`
2. Proof it with `which_structure`
3. depending on the answer, replace the `()` for `{}` or `[]` with the `string_replace_index` function.
4. Rinse ande repeat until there is no `()` lasting

### 4. Parsing and decoding

If we simple decode the stings, newlines, quotes and other things could mess up with the parser (there is no easy way to escape all teh necessary quotes, and in a code string there is no difference between a newline in a string and a physical newline).

So this will feel a little hacky.

#### Preparation

You will need an _empty_ dictionary to save the translations for the decoding.

#### Procedure

Capture all the strings on a list. At this point, all strings are encoded and single quoted. Loop through this list:

1. gerenrate an unique number `k` (could be sequential)
2. Add to the dictionary the pair `k:decoded`, where `decoded` is de decoded string (no quotes)
3. replace the encoded string on the text _including the quotes_, and put in its place a call to your dictionary with key `k`.

Once this is done for each string on the text, you can just `eval()` the result. Since we scaped everything, and every `()` and unquoted text was examined, there is no security risk on this eval.

## Dump a `dict` on PyON format

### 1. First substitutions to the string form

#### Ingredients

* `complex` parenthesized numbers pattern: `\((\d+(?:\+|\-)\d+j)\)`. Python string representation of non-imaginary complex is `({re}+{im}j)`, with the parenthesis.

* The `string` pattern from the Load recipe

* `string_literal_encode` from the Load recipe


#### Procedure

1. Take the string form of the desired dict to dump

1. Encode string literals, just as in the Load recipe

1. De-parenthesize the non-imaginary complex numbers with the `complex` pattern

1. Erase all spaces

1. Convert python `[]` and `{}` structures to indent-dedent `()` tokens, separated by spaces, i.e. `'{'` will be replaced by `' ( '`

### 2. Reestructuring

#### Preparation

You will need an empty list to store the processed lines, a zero counter for the indentation level, and a place to save the last line (unprocessed). This las variable should be initialized at something, maybe a space.

#### Procedure

Split the result from step 1 at every space (we put all those spaces in step 1.5) or comma. Iterate through that list:

1. If the element is an indent token `(`:
	* If the last element was a dedent token `)`, put a `level` indented comma into the processed lines list.
	* Increase the level counter
1. If the element is a dedent token `)`, decrease the level counter.
1. If is anything else, add it to the procesed lines with proper indentation level.

At the end, join the processed lines, separated by `\n`. It is recommended to use `"\n".join(.....)`

### 3. Decoding

#### Ingredients

* `string_escape(s:str) -> str` function, that escapes all quotes, and unscapes `\\n` and `\\t`.
* `string` pattern from the Load recipe
* `url_decode` from the Load recipe
* `literal_string_decode(match:re.match) -> str`, the copmplement of the function from the Load recipe:
	* `string` is the second capture group, but passed through `url_decode` and `string_escape` functions.
	* `kind` is initially the first capture group, but is turned into `'''` if `string` has any `\n`
	* Returns `kind+string+kind`.

#### Procedure

Substitute strings using the `literal_string_decode` function in `re.sub`.

The result is a string with the initial dictionary in PyON notation.
