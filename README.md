# Niko Programming Language
An *Experimental Programming Language* written **Python**.
It uses **Top Down Operator Precedence** aka, **Pratt Parser** for parsing.

This project should only be used for educational purposes

## Project Structure

Source code split into three files:
* `lexer.py`  generates tokens ready for parsing
* `parse_tree.py` generates parse_tree 
* `interpreter.py` interprets the tree

Main focus of the project is `parse_tree.py` because this project is essentially an implementation of **TDOP** Algorithm. 
The interpreter code is realy simple. Actualy just one function. (in `interperter.py`)

## Using The Language
In the `test-code` file, there are many examples. Syntax is very similar to python. Code can be used as: 

`python3 interpreter.py test-code/{file_name}`

## Hacking the language
This language implementation can be used for educational purposes. The code can be very simple however for realy understanding the parser algorithm look at the Fredrik Lundh's implementation. He does not implements the interpreter but you can check mine for it.

## Reference
[Fredrik Lundh's implementation](http://effbot.org/zone/simple-top-down-parsing.htm)

[Douglas Crockford's implementation](http://www.crockford.com/). Uses javascript however the algorithm is the same.

[Turkish resource, Yaşar Arabacı](https://ysar.net/python/lexical-analiz.html) Best lexer implementation. Also There is parser too


