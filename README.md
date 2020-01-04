# Niko Programming Language
An *Experimental Programming Language* written **Python**.
It uses **Top Down Operator Precedence** aka, **Pratt Parser**.

This project should only be used for educational purposes

## Project Structure

Source code split into three files:
* `lexer.py`  generates tokens ready for parsing
* `parse_tree.py` generates parse_tree 
* `interpreter.py` interprets the tree

Main focus of the project is `parse_tree.py` because this project is essentially an implementation of **TDOP** Algorithm. 
Making an interpreter requires much more work. The code in the interpreter file is shitty and I currently have o plans on improving it.
I am making a new language with Rust Language. How ever not yet published it. 

## Using The Language
In the `test-code` file, there are many examples. Syntax is very similar to python. Code can be used as: 

`python3 interpreter.py test-code/{file_name}`


## Reference
[Fredrik Lundh's implementation](http://effbot.org/zone/simple-top-down-parsing.htm)
[Douglas Crockford's implementation](http://www.crockford.com/). However uses javascript but algorithm is the same.
[Turkish resource, Yaşar Arabacı](https://ysar.net/python/lexical-analiz.html) Best lexer implementation. Also There is parser too

*[TDOP]:Top Down Operator Precedence

