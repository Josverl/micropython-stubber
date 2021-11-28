
# Developing

## Cloning the repo 
The repo uses two submodules in order to generate the MicroPython frozen stubs.
in order to fully check-out the repo you need to run additional commands 
how to clone : 
``` bash
git submodule init
git submodule update --recursive
```

how to add : 
``` bash
git submodule add --force -b master https://github.com/micropython/micropython.git 
git submodule add --force -b master https://github.com/micropython/micropython-lib.git 
```


## Windows 10 
I use Windows 10  and use WSL2 to run the linux based parts. 
if you develop on other platform, it is quite likely that you may need to change some details. if that is needed , please update/add to the documentation and send a documentation PR.

* clone 
* create python virtual environment (optional) 
* install requirements-dev 
* setup sister repos
* run test to verify setup 

## Github codespaces 

Is is also possible to start a pre-configure development environment in [GitHub Codespaces](https://github.com/features/codespaces)
this is probably the fastest and quickest way to start developing.

Note that Codespaces is currently in an extended beta. 
```{image} img/codespaces.png
:alt: picture of how to start codespaces
:width: 300px
```


## Wrestling with two pythons 

This project combines CPython and MicroPython in one project.  As a result you may/will need to switch the configuration of pylint and VSCode to match the section of code that you are working on.  This is caused by the fact that pylint does not support per-folder configuration 

to help switching there are 2 different .pylintrc files stored in the root of the project to simplify switching.

Similar changes will need to be done to the .vscode/settings.json 

If / when we can get pylance  to work with the micropython stubs , this may become simpler as 
Pylance natively supports [multi-root workspaces](https://code.visualstudio.com/docs/editor/multi-root-workspaces), meaning that you can open multiple folders in the same Visual Studio Code session and have Pylance functionality in each folder.

## Minification 

If you make changes to the createstubs.py script , you should also update the minified version by running `python process.py minify` at some point.

If you forget to do this there is a github action that should do this for you and create a PR for your branch.

## Testing 

MicroPython-Stubber has a number of tests written in Pytest

see below overview

| folder        | what                                               | how                                                          | used where              |
| ------------- | -------------------------------------------------- | ------------------------------------------------------------ | ----------------------- |
| board         | createstubs.py<br />normal & minified              | runs createstubs.py on micropython-linux ports               | WSL2 and github actions |
| checkout_repo | simple_git module<br />retrieval of frozen modules | does not use mocking but actually retrieves different firmware versions locally using git or dowNloads modules for online | local windows           |
| common        | all other tests                                    | common                                                       | local + github action   |

```{note}
Also see [test documentation](testing.md)
```

**Platform detection to support pytest**
In order to allow both simple usability om MicroPython and testability on Full Python,
createstubs does a runtime test to determine the actual platform it is running on while importing the module
This is similar to using the `if __name__ == "__main__":` preamble 
If running on MicroPython,
    then it starts stubbing 

``` python
if isMicroPython():
    main()
```



**Testing on micropython linux port(s)**
In order to be able to test `createstubs.py`, it has been updated to run on linux, and accept a --path parameter to indicate the path where the stubs should be stored.

## Debugging Cpython code that run Micropython 

Some of the test code run the micropython executable using `subprocess.run()`.
When you try to debug these tests the VSCode debugger (debugpy](https://github.com/microsoft/debugpy) then tries to attach to that micropython subprocess in order to facilitate debugging.
This will fail as reported in this [issue](https://github.com/microsoft/debugpy/issues/781).  

The solution to this problem is to disable subprocess debugging using the `"subProcess": false` switch.

``` json 
// launch.json
        {
            // disable pytest coverage report as it conflicts with debugging tests
            "name": "Debug pytest tests",
            "type": "python",
            "purpose": [
                "debug-test"
            ],
            "console": "integratedTerminal",
            "justMyCode": false,
            "stopOnEntry": false,
            "subProcess": false, // Avoid debugpy trying to debug micropython
            "env": {
                "PYTEST_ADDOPTS": "--no-cov"
            }
        },
```

## github actions

### pytests.yml 

This workflow will :

- test the workstation scripts 

- test the createstubs.py script on multiple micropython linux versions 

- test the minified createstubs.py script on multiple micropython linux versions 

### run minify-pr.yml

This workflow will :

- create a minified version of createstubs.py 

- run a quick test on that 

- and submit a PR to the branch <branch>-minify

