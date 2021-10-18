# Testing

A significant number of tests have been created in pytest.
- The tests are located in the `tests` folder. 
- The `tests/data` folder contains folders with subs that are used to verify the correct working of the minification modules
- debugging the tests only works if --no-cov is specified for pytest


## testing & debugging createstubs.py 

- the `tests\mocks` folder contains mock-modules that allow the micropython code to be run in CPython. This is used by the unit tests that verify `createstubs.py` and it minified version.

- in order to load / debug the test the python path needs to include the cpython_core modules (Q&D) 
- mocking cpython_core/os is missing the implementation attribute so that has been added (Q&D)  

## platform detection

In order to allow both simple usability om MicroPython and testability on *full* Python,
createstubs does a runtime test to determine the actual platform it is running on while importing the module

This is similar to using the `if __name__ == "__main__":` preamble  

``` python
if isMicroPython():
    main()
```

This allows pytest test running on full Python to import `createstubs.py` and run tests against individual methods, while allowing the script to run directly on import on a MicroPython board. 

```{note}
Some test are platform dependent and have been marked to only run on linux or windows
```

## Code Coverage 
Code coverage is measured and reported in the `coverage/index.html` report.
This report is not checked in to the repo, and therefore is only 