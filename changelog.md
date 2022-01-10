
# changelog 
# Naming convention
- use {family}-v{version}-{port} notation across all scripts and tools
- updated documentation accordingly 
- single function to handle version names in various formats (clean_version)
- requirements: pin dependencies to avoid differences when running acriss multiple machines.
- get_mpy_frozen: 
    - refactor module
    - checkout the matching commit of micropython-lib 
      withouth this it is not possible to build stubs older versions due to a restructure of micropython-lib
- bulk_stubber: 
    - make more robust by including depedencies in the project.
    - detect pyboard based on USB VID & PID
    - prep autostubber for pybv11
- manifest.json generation
    - improve core manifest.json information 
    - improve support for grouping and sorting 
- createstubs: v1.5.1
    - get_root can detect /sd cards
    - sample bootfile works on pyb1.1, esp323, esp8266

## generate stubs from documentation 

## betterstubs branch
- createstubs  - version 1.3.16
    - fix for 1.16 
    - skip _test modules in module list
    - black formatting 
    - addition of __init__ methods ( based on runtime / static)
    - class method decorator 
    - additional type information for constants using comment style typing
    - detect if running on MicroPython or CPython
    - improve report formatting to list each module on a separate line to allow for better comparison

- create stubs from micropython documentation
    - Read the micropython library documentation files 
    - Extract 
        modules
            functions
            classes  (some classes are described as functions and need to be hoisted up to a class)
                methods
                class methods
                static methods
            exceptions
    - extract the relevant docstrings
    - determine the return type of a function or method based on the docstring 
        this is about 60% accurate 


- workflows
    - move to ubuntu 20.04 
        - move to test/tools/ubuntu_20_04/micropython_v1.xx
    - run more tests in GHA 

- postprocessing 
    - minification adjusted to work with `black`
    - use `mypy.stubgen` to generate stubs 
    - remove dependency and 'make_stub_files.py' as this is no longer maintained and has several issues.
    - run per folder 
        - verify 1:1 relation .py-.pyi
        - run `mypy.stubgen` to generate missing .pyi files
    - publish test results to GH



- develop / repo setup
    - updated dev requirements (requirements-dev.txt)
    - seperate install needed for:
        - git 2.23 .0 or newer (git switch)
        - pyright via npm install (and thus npm)
    - switched to using submodules to remove  external dependencies
        how to clone : 
        `git submodule init`
        `git submodule update`
    - enable developing on [GitHub codespaces](https://github.com/codespaces)
        - add configuration for codespaces 
        - devcontainer
            - installs pyright ( via `npm install -g pyright`)
            - starts .devcontainer/setup.h
        - setup.sh 
            - initializes the submodules 
            - installs python requirements-dev.txt 
            - installs python requirements-dev.txt 

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
`
    - 


