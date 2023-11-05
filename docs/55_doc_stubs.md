# Documentation Stubs  

## What / Why 

Advantages : they bring the richness of the MicroPython documentation to Pylance.
This includes function and method parameters and descriptions, the module and class constants for all documented library modules.
  

## How docstubs are generated
The documentation stubs are generated using the `stubber get-docstubs` command.

1) Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking
using a custom-built parser to read and process the micropython RST files
- This will generate :
    - Python modules (`<module.py>`), one for each `<module>.rst` file
        - The module docstring is based on the module header in the .rst file

    - Function definitions 
        - Function parameters and types based on documentation
          As the parameter documentaion is sometimes rather abigious or imprecise, the parameters definities are cleaned up based on a hand tuned algoritm
        - The function docstring is based on the function description in the .rst file
        - The return type of a function is based on phrases used in the documentation, with an override table for functions with insufficient documented information to determine the return type. 

    - Classes
        - The class docstring is based on the Class description in the .rst file
        - __init__ method
            - The init parameters are based on the documentation for the class 
              As the parameter documentaion is sometimes rather abigious or imprecise, the parameters definities are cleaned up based on a hand tuned algoritm
            - __init__ docstring is based on the Class description in the .rst file
        - Methods
            - Method parameters and types based are based on the documentation in the .rst file
              As the parameter documentaion is sometimes rather abigious or imprecise, the parameters definities are cleaned up based on a hand tuned algoritm
            - The method docstring is based on the method description in the .rst file
            - The return type of a method is based on phrases used in the documentation, with an override table for functions with insufficient documented information to determine the return type.         
            - Method decorators @classmethod and  @staticmethod are generated based on the use of `py:staticmethod` or `py:classmethod` in the documentation.
              ref: https://sphinx-tutorial.readthedocs.io/cheatsheet/
            - Method parameter names `self` and `cls` are used accordingly. 

    - Exceptions

### Return types
- Tries to determine the return type by parsing the docstring.
    - Imperative verbs used in docstrings have a strong correlation to return -> None
    - Recognizes documented Generators, Iterators, Callable
    - Coroutines are identified based tag "This is a Coroutine". Then if the return type was Foo, it will be transformed to : Coroutine[Foo]
    - A static Lookup list is used for a few methods/functions for which the return type cannot be determined from the docstring. 
    - add NoReturn to a few functions that never return ( stop / deepsleep / reset )
    - if no type can be detected the type `Any` is used

### Lookup tables : 
 - [src/stubber/rst/lookup.py](src/stubber/rst/lookup.py)
     - LOOKUP_LIST
        - contains return types for functions and methods 
        - "module.[class.].function" : ( "type", probability)
    - NONE_VERBS
        - if no type has been determined, and the docstring starts with one of these verbs, then assume the return type is None
    - MODULE_GLUE
        - Add additional imports to some  modules to allow one module to import other supporting modules
        - currently only used for `lcd160cr` and `esp32`
    - PARAM_FIXES 
        - manual fixes needed for parameters ( micropython v.16 & v1.17)
        - used to clean up  the parameter strings before further interpetation using search and replace
    - CHILD_PARENT_CLASS
        - List of classes and their parent classes that should be added to the class definition. The documentation contains no clear references of the parent classes so these can only be added based on a (manual) lookup table
        - Note:  The parent class **Exeptions** is determined based on the rst hint `py:exception` and the Class Name.

### Code Formatting
The generated stub files (`.py`) are formatted using `black` and checked for validity using `pyright`

Note: black on python 3.7 does not like some function defs, this is not treated as an error. 
    `def sizeof(struct, layout_type=NATIVE, /) -> int:` 


### Ordering of inter-dependent classes in the same module   
Classes are frequently documented in a different order than thery need to be declared in a source file.
To accomodate for this the source code is re-ordered to avoid forward references in the code.
The code for this is located in :
- [src/stubber/rst/classsort.py](src/stubber/rst/classsort.py)
- [src/stubber/rst/output_dict.py](src/stubber/rst/output_dict.py)


### Add GLUE imports to allow specific modules to import specific others. 
  This is based on the `MODULE_GLUE` table to support some modules that need to import other modules or classes.



### Literals / constants
    - documentation contains repeated vars with the same indentation
    - Module level:
    .. code-block:: 

        .. data:: IPPROTO_UDP
                  IPPROTO_TCP

    - class level: 
    .. code-block:: 
    
        .. data:: Pin.IRQ_FALLING
                  Pin.IRQ_RISING
                  Pin.IRQ_LOW_LEVEL
                  Pin.IRQ_HIGH_LEVEL

                  Selects the IRQ trigger type.

    - literals documented using a wildcard are added as comments only 


- Repeats of definitions in the rst file for similar functions or literals
    - CONSTANTS ( module and Class level )
    - functions
    - methods
