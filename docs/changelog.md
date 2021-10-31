
# Changelog 

## createstubs - Minified- v1.4.1 
- Switched to use [python-minifier](https://github.com/dflook/python-minifier) for the minification due to the end-of-life of the previous minification tool 
  The new minification tool produces more compact code, although that is still not sufficient for some memory constrained devices.
  - there are no functional changes, 
  - the detection of Micropython was adjusted to avoid the use of eval which blocked a minification rule
  - several tests were adjusted

## documentation 
- Add Sphinxs documentaion 
    - changelog 
    - automatic API documentation for 
        * createsubs.py (board) 
        * scripts to run on PC / Github actions
- Publish documentation to readthedocs
    
## createstubs - v1.4-beta

- createstubs.py
    - improvements to handle nested classes to be able to create stubs for lvgl.
    this should also benefit other more complex modules.

- added `stub_lvgl.py` helper script

## createstubs.py  - v1.3.16

- createstubs.py
    - fix for micropython v1.16 
    - skip _test modules in module list
    - black formatting 
    - addition of __init__ methods ( based on runtime / static)
    - class method decorator 
    - additional type information for constants using comment style typing
    - detect if running on MicroPython or CPython
    - improve report formatting to list each module on a separate line to allow for better comparison

- workflows
    - move to ubuntu 20.04 
        - move to test/tools/ubuntu_20_04/micropython_v1.xx
    - run more tests in GHA 

- postprocessing 
    - minification adjusted to work with `black`
    - use `mypy.stubgen`
    - run per folder 
        - verify 1:1 relation .py-.pyi
        - run `mypy.stubgen` to generate missing .pyi files
    - publish test results to GH


- develop / repo setup
    - updated dev requirements (requirements-dev.txt)
    - enable developing on [GitHub codespaces](https://github.com/codespaces)
    - switched to using submodules to remove  external dependencies
        how to clone : 
        `git submodule init`
        `git submodule update`
    - added black configuration file to avoid running black on minified version
    - switched to using .venv on all platforms
    - added and improved tests
        - test coverage increased to 82%
    - move to test/tools/ubuntu_20_04/micropython_v1.xx
        - for test (git workflows)
        - for tasks 
    - make use of CPYTHON stubs to alle makestubs to run well on CPYTHON
        - allows pytest, and debugging of tests
    - add tasks to :
        - run createstubs in linux version
        

