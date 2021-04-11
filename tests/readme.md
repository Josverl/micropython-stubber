# testing / debugging createstubs.py 

- debugging the tests only works if --no-cov is specified for pystest
- in order to load / debug the test the python path needs to include the cpyton_core modules (Q&D) 
- mocking cpyton_core/os missins the implementation attribute so that has been added (Q&D)  


# platform detection

In order to allow both simple usability om MicroPython and testability on Full Python,
createsubs dos a runtimne test to determin the actual platform it is runnin on while importing the module
This is similar to using the `if __name__ == "__main__":` preamble 
if  running on MicroPython,
    then start stubbing 

``` python
if isMicroPython():
    main()
```

this allows Test running on full Python to import `createstubs.py` and run tests against individual methods

# 
Some test are platfrom dependend and have been marked as such 


