# Documentation Stubs  

## What / Why 

Advantages : they bring the richness of the MicroPython documentation to Pylance.
This includes function and method parameters and descriptions, the module and class constants for all documented library modules.
  

## How 
The documentation stubs are generated using `src/stubs_from_docs.py`

    Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking 
    using a custom-built parser to read and process the micropython RST files
    - generates:
        - modules 
            - docstrings

        - function definitions 
            - function parameters based on documentation
            - docstrings

        classes
            - docstrings
            - __init__ method
            - parameters based on documentation for class 
            - methods
                - parameters based on documentation for the method
                - docstrings

        - exceptions

    - tries to determine the return type by parsing the docstring.
        - Imperative verbs used in docstrings have a strong correlation to return -> None
        - recognizes documented Generators, Iterators, Callable
        - Coroutines are identified based tag "This is a Coroutine". Then if the return type was Foo, it will be transformed to : Coroutine[Foo]
        - a static Lookup list is used for a few methods/functions for which the return type cannot be determined from the docstring. 
        - add NoReturn to a few functions that never return ( stop / deepsleep / reset )
        - if no type can be detected the type `Any` is used

    The generated stub files are formatted using `black` and checked for validity using `pyright`
    Note: black on python 3.7 does not like some function defs 
    `def sizeof(struct, layout_type=NATIVE, /) -> int:` 

    - ordering of inter-dependent classes in the same module   
    
    - Literals / constants
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

    - add GLUE imports to allow specific modules to import specific others. 

    - repeats of definitions in the rst file for similar functions or literals
        - CONSTANTS ( module and Class level )
        - functions
        - methods

    - Child/ Parent classes
        are added based on a (manual) lookup table CHILD_PARENT_CLASS

### 