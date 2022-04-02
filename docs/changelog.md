
# Changelog 

# v1.6.4
- unified different scripts into a single CLI tool
- replace submodules with `stubber clone` command


## Tests
- add more clone test variants
- fix incorrect mock
- add minify mock tests
- change coverage reporting to codecov only

## Configuration 
- add configuration option via in pyproject.toml
- use config.stub_path for all-stubs
- use typed config
- use configured repo path everywhere

## stubber cli 
- usr -t for --tag
- make VERSION_LIST robust
- gracefully handle get tags from non-exitant folder
- use dynamic version  list
- add git switch

## common: 
- basicgit: accept Paths
- add checkout version, refactor config and version
- refactor postprocessing

## Github Actions
wf: run stubber clone before tests


# v1.6.3 minor cleanups

## cli: 
- improve help
- add update-fallback to cli
- update toml with config
- refactor functions from cli to utils
- refactor utils
- use repo path
- default clone to repos folder
- add version and logging control
-  change cmd  `init` to `clone`

## Tests
- testspace: change codecov report type
- refactor and improve tests & mocks

## Developing:
devcontainer: add git graph extension


# v1.6.0

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


## stubber cli: 
-  add init test & refector imports
-  fix tests
-  merge docstubs into stubber
-  reduce tests
-  merge get-all-stubs into stubber
-  merge get_all_stubs into stubber
-  add init
-  add stub and some tests
-  refactor minify and add -all option

##  config
- change to use module tomlli(b)
## common: 
- update pyright config to reduce noise

## firmware stubber
fw-stubber: clean up excepts

## Documentation 
docs: fix tomllib
docs: document the CLI for stubber using sphinx-click
readme: add badges for pypi and codecov
doc updates
fix docbuild for poetry
update totdos in source

docstubs: fix json import
fix: black formatting across platforms

add settings and script for coverage reporting
update snippets
(origin/dev/snippets) snippets:add checks

Develop: 
fix: codespace poetry setup

#test 
test: fix fewer arguments
tests: add firmware stubber version tests
test: add missing toml
test: add package == version == firmware stubber version tests
test: basicgit - add mocktest  git
test: fix minify test remove unused imports

## Github Actions:
wf: use poetry run and poetry install 

pkg: updates to support poetry
wf: poetry install verbose
pkg: update actions to work with poetry
pkg: Move all stubber files into module folder
pkg: get version from poetry package
pkg: move csv into package
config: remove pylance config from vscode settings
pkg: add data files

# Use Poetry 

## Dependencies 
- bump distro from 1.6.0 to 1.7.0
- bump pytest from 6.2.5 to 7.0.1
- bump myst-parser from 0.16.1 to 0.17.0
- bump coverage from 6.3 to 6.3.1
- bump black from 21.12b0 to 22.1.0
- bump libcst from 0.3.23 to 0.4.1
- bump pytest-mock from 3.6.1 to 3.7.0
- bump mpy-cross from 1.17 to 1.18

## documentation 
- Add notes to docstrings/descriptions
- (bluetooth_constants) doc: configure submodules
- docs: add open in VSCode banner
- textual and updates to version notation
- Update 40_firmware_stubs.md

## docstubs: 
- fix optional - Optional Parameters are not treated as optional https://github.com/Josverl/micropython-stubber/issues/183
- add docstubs validation
- skip 3 stubs.
- create umodules https://github.com/Josverl/micropython-stubber/issues/176
- allign to micropython PR and update tests
- workaround for re.Match and smarter tests
- fix module & Class constant handling & tests
- Add `= ...` to module and class level constants to avoid errors when they are used as a default value in function of nethod

## scripts:
- script update_modulelist, - write updates to:         - board/modulelist.txt         - board/createsubs.py
- bulk_stubber: Copy generated/firmwarestubs to all-stubs/* use firmware-stubs path for temp storage
- Update BulkStubber & getserial for esp32, esp8266 and stm32
- minify.ps1: posix paths
- bulkstubber: more versions

## Common
- improve black formatting for subfolders
- utils: do not use BaseException
- config: pycache
- data: add firmware modules
- Multi-root with mpy-stdlib based on pico-go
- utils.stubgen: re-apply refactor to avoid use of os.cmd or subprocess.run
- utils.stubgen: refactor to avoid use of os.cmd or subprocess.run

## Validation
- add snippets to test mpy stdlib
- validation: Add more snippets
- update validation snippets
- WS with pyright snippets

## Github Actions:
- wf: do not run minified tests twice, minify all

## Developing:
devcontainer: also init git submodules
devcontainer: change python setup

## Tests
test: fix test_socket _class
test: fix return type and test deepsleep
test: skip test_createstubs on  windows + python 3.7
test: native test on windows, include db test on linux
test: add createstubs_db on all platforms
test: lower theshold to  25 stubs
test: add native integration test for micropython_mem
test: linux rest on ubuntu and debian, seperate branch / fail logic in docstubs test
test: add additional firmwares
test: waste less time in by reducing test size
test: remove path test
debug: fix debug config for tests
debug: add missing debug property
test: fix pessimistic test and make more robust


# createsubs v1.5.4 
Better exeptions fix missed updates to mem and stub variants

## Change naming convention:
- board: user {family}-v{version}-{port} notation
- change name of master branch to main

## stubber cli
- fix: - rp2.PIO.irq
- fix dequeue
- revert re.match change
- fixup re.match
- add fixes for remaining Documentation errors
- generate Exception Classes
- fix test and default for machine.Pin.__init__
- fix 3 Non-default argument follows default argument errors
- run pyflake to remove unused imports
- fix black parameters
- no need to redefine Exception
- use 'Latest' as a version tag for the most recent master
- use v for version


## Common
- pyright: restore exec environments test & board
- get_frozen: improve  force __init__.py
- get_frozen: run black on new/updated stubs
- createstubs: support for RP2 , and accept kwargs for methods and functions
- lobo: skip some modules
- get_mpy: match_lib - add v1.18 rename to .csv
- version: latest
- basicgit: remove debugging code
- basicgit: fix gettag 'latest'
- bulk_stubber: make more robust by adding the dependencies to the repo
- get_frozen: clean collected modules - freeze to empty directory - block CI/CD manifest
- get_mpy: for frozen modules: checkpout the matching commit of micropython-lib
- mpy_frozen: refactor module
- process: --source allows scriptname to be specified & add mpy-cross step
- update_pyi : rename and more efficient updating find .pyi`s created in the wrong location and move them
- Manifiest:  release is optional
- use __version__ and bump version
- get_mpy: improve porcessing of frozen modules V1.16  and newer
- schema: change stubtype property
- Module manifest: Sorting and add port name
- update get-frozen
- improve frozen manifest processing  (#88)
- utils: update clean version
- createstubs* : Add stubtype to manifest - remove redundant try/catch
- process.py: cleanup unused variables
- process.py: use click

## scripts
- add scripts to simplify copy and updates
- Merge generate stubs from documentation

## Firmware stubber 
- createstubs: sample bootfile works on pyb & esp
- createstubs:  get_root can detect /sd cards

## Dependencies 
- python requirements: pin versions
- bump coverage from 6.2 to 6.3
- bump sphinx from 4.3.2 to 4.4.0
- add autoflake
- bump mpy-cross from 1.16 to 1.17
- bump myst-parser from 0.15.2 to 0.16.1
- bump mypy from 0.930 to 0.931
- bump sphinx from 4.3.1 to 4.3.2
- bump rshell from 0.0.30 to 0.0.31

## Documentation 
- docs: update naming convention
- fix stuborder image
- Update 10_approach.md
- Naming convention
- one less
- add branch rename instructions
- documented Docs to Stubs process

## validation
- basic setup for stub validation
- add code snippets for validation

## BugFixes: 
- fix: ensure that `from __future__ ...` is at start
- add .pyi stubs for umqtt.robust Workaround for missing __init__.py in source
- fix: allow stubgen of async yield in stub (python 3.6) closes #137
- fix Exception lineskip
- fix: get_mpy - save&resore  cwd
- fix lobotest to match reduced modules
- Fix core module sort order closes #68


## Github Actions:
- wf test: ensure artefact upload on error
- wf: report coverage
- testspace: use folders
- pytest: upload to testspace
- wf: allign naming

## Scripts:
- prep autostubber for pybv11
- detect pyboard

## code quality: 
- fix warnings
- improve core manifest.json

## Tests
- test: fix testregression for latest version
- tests: docstubs improve test of class documented as function
- testspace script
- test: add mpy-cross test and split to seperate folder
- improve grouping
- pytest - use matrix.os in test results
- test: do not run pytest-cov
- tests: drop utf-8 encoding
- test : init logging
- test : fix path
- test: stabelize pyright & black detection
- tests: skip  basicgit tests
- add integration tests for cmdline



# improve docstubs 
- rst: cleaner import though use of __all__
- document: debug subProcess
- docstubs: fix random.choice(): Any
- docstubs: workaround black on Py3.7

## common:
- add header to modulelist
- devcontainer: simpler requirements
- utils: fix  generating .pyi files from .py files with errors
- fix: remove duplication fix minor issues
- github: group logging

# Tests
- pin python version
- pytest: add test markers
- change ubuntu version detection to codename
- add mark.minfied to linux tests add new platform markers
- implement workaround for failing minified tests
- tests: restructure board test to share testdata
- add debug config
- tests: fix minified tests
- tests: improve & merge testing
- test: linux detection++
- tests: use pathlib and fix paths
- clarify intentional error
- remove duplicate tests
- tests: Restucture Micropython on Cpython tests
- tests: resolve issues due to sloppy imports in tests
- stubgen test : add logging for python 3.7

## minify: 
- minify all variants
- also remove _log * lines
- also: minimize createstubs_mem.py
- Fix: remove duplicate builtins from minified
- minify : fix mpy-cross on Python 3.7

## createstubs:
- add normal and mem_constrained versions
- add database variant
- Save state to database and reboot on memory error
- reduce complexity from createstubs to save ram possibly loosing some edge cases ++ docs
- update to handle multi-file uploads to overcome  esp8266 memory constraints
- both normal and db work on esp8266 (report not done)
- keep get_root and _info to allow for testing
- update tests to clean-up  sys.path after the tests
- keep __version__ in minified
- use __version__ move unneeded import of machine
- gracefully handle missing `modules.txt`
- stubber: fix firmwareid for mpy esp8266
- stub_lvgl: fix __version__


## Github Actions:
- use posix path
- workflow: test : on checkout fetch all branches and tags

## Docs: 
- do not keep generated API Docs
- refactor documenation to more docs
- add explanation om memory optimization.
- add cloning of submodules
- safer path insertion

## Other : 
- add remote_stubber script
- bulk_stubber: run black formatter after all downloads
- remote_stubber: improve reporting
- bulk stubber: make esp8266 work more reliable ESP32 WIP - scrips fail to upload




# createstubs: v1.5.1
    - get_root can detect /sd cards
    - sample bootfile works on pyb1.1, esp323, esp8266

## Documentation Stubs 

- avoid the use of BaseException

## createstubs.py - v1.4.3
- significant memory optimisation for use on low-memory devices such as the esp8266 family
  - load the list of modules to be stubbed from a text file rather than as part of the source 
  - use both minification and the `mpy-cross` compiler to reduce the claim on memory (RAM) 

```{warning}
This is a potential breaking change for external tools that expect to either directly execute the script or upload only a single file to an MCU in order to stub.
```
- the current process is automated in [`remote_stubber.ps1'][remote_stubber]
## createstubs.py - v1.4.2
- Fixes a regression introduced in 1.4-beta where function definitions would include a self parameter. 

## minified createstubs.py - v1.4.1
- Switched to use [python-minifier](https://github.com/dflook/python-minifier) for the minification due to the end-of-life of the previous minification tool 
  The new minification tool produces more compact code, although that is still not sufficient for some memory constrained devices.
  - there are no functional changes, 
  - the detection of Micropython was adjusted to avoid the use of eval which blocked a minification rule
  - several tests were adjusted

## documentation 
- Add Sphinxs documentation 
    - changelog 
    - automatic API documentation for 
        * createstubs.py (board) 
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
        

[remote_stubber]: ./65_scripts.md#remote_stubber.ps1