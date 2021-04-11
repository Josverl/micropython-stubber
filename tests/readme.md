

# testing / debugging createstubs.py 

- debugging the tests only works if --no-cov is specified for pystest
- in order to load / debug the test the python path needs to include the cpyton_core modules (Q&D) 
- mocking cpyton_core/os missins the implementation attribute so that has been added (Q&D)  

# 
Some test are platfrom dependend and have been arked as such 
