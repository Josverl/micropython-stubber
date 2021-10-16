# testing / debugging createstubs.py 

- debugging the tests only works if --no-cov is specified for pytest
- in order to load / debug the test the python path needs to include the cpython_core modules (Q&D) 
- mocking cpython_core/os is missing the implementation attribute so that has been added (Q&D)  


# platform detection

In order to allow both simple usability om MicroPython and testability on Full Python,
createstubs does a runtime test to determine the actual platform it is running on while importing the module
This is similar to using the `if __name__ == "__main__":` preamble 
if  running on MicroPython,
    then start stubbing 

``` python
if isMicroPython():
    main()
```

this allows Test running on full Python to import `createstubs.py` and run tests against individual methods

# 
Some test are platform dependent and have been marked as such 


