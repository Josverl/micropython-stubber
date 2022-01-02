# References 

## Inspiration 

### Thonny - MicroPython _cmd_dump_api_info  _[MIT License]_

The `createstubs.py` script to create the stubs is based on the work of Aivar Annamaa and the Thonny crew.
It is somewhere deep in the code and is apparently only used during the development cycle but it showed a way how to extract/generate a representation of the MicroPython modules written in C

While the concepts remain,  the code has been rewritten to run on a micropython board, rather than on a connected PC running CPython.
Please refer to :  [Thonny code sample](https://github.com/thonny/thonny/blob/786f63ff4460abe84f28c14dad2f9e78fe42cc49/thonny/plugins/micropython/__init__.py#L608)


### MyPy Stubgen

[MyPy stubgen](https://github.com/python/mypy/blob/master/docs/source/stubgen.rst#automatic-stub-generation-stubgen) is used to generate stubs for the frozen modules and for the `*.py` stubs that were generated on a board.  

### make_stub_files _[Public Domain]_ 

https://github.com/edreamleo/make-stub-files

This script `make_stub_files.py` makes a stub (.pyi) file in the output directory for each source file listed on the command line (wildcard file names are supported). 

The script does no type inference. Instead, the user supplies patterns in a configuration file. The script matches these patterns to:
The names of arguments in functions and methods and
The text of return expressions. Return expressions are the actual text of whatever follows the "return" keyword. The script removes all comments in return expressions and converts all strings to "str". This preprocessing greatly simplifies pattern matching.

```{note}
It was found that the stubs / prototypes of some functions with complex arguments were not handled correctly,
resulting in incorrectly formatted stubs (.pyi)  
Therefore this functionality has been replaced by MyPy `stubgen` 
```
## Documentation on Type hints

- [Type hints cheat sheet](https://github.com/python/mypy/blob/master/docs/source/cheat_sheet_py3.rst#type-hints-cheat-sheet-python-3)

- [PEP 3107 -- Function Annotations](https://www.python.org/dev/peps/pep-3107/)
- [PEP 484 -- Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [Optional Static Typing for Python](https://github.com/python/mypy#mypy-optional-static-typing-for-python)
- [TypeShed](https://github.com/python/typeshed/)
- [SO question](https://stackoverflow.com/questions/35602541/create-pyi-files-automatically)


[stubs-repo]:   https://github.com/Josverl/micropython-stubs
[stubs-repo2]:  https://github.com/BradenM/micropy-stubs
[micropython-stubber]: https://github.com/Josverl/micropython-stubber
[micropython-stubs]: https://github.com/Josverl/micropython-stubs#micropython-stubs
[micropy-cli]: https://github.com/BradenM/micropy-cli
[using-the-stubs]: https://github.com/Josverl/micropython-stubs#using-the-stubs
[demo]:         docs/img/demo.gif	"demo of writing code using the stubs"
[stub processing order]: docs/img/stuborder_pylance.png	"recommended stub processing order"
[naming-convention]: #naming-convention-and-stub-folder-structure
[all-stubs]: https://github.com/Josverl/micropython-stubs/blob/main/firmwares.md
[micropython]: https://github.com/micropython/micropython
[micropython-lib]:  https://github.com/micropython/micropython-lib
[pycopy]: https://github.com/pfalcon/pycopy
[pycopy-lib]: https://github.com/pfalcon/pycopy-lib
[createstubs-flow]: docs/img/createstubs-flow.png
[symlink]: #create-a-symbolic-link

