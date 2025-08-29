# Using Micropython stubber 

This section describes how to use micropython-stubber to create and maintain stubs for a MicroPython firmware or project.

If you just want to use the stubs, then you can skip this section and instead read the documentation in the sister-repo [micropython-stubs][] section [using-the-stubs][] 

## Quick Start for Standard Releases

For official MicroPython releases, follow the standard workflow:

```bash
pip install micropython-stubber
stubber clone --add-stubs
stubber switch v1.22.2
stubber get-docstubs
stubber get-frozen
```

## Custom MicroPython Builds

If you're working with a fork, branch, pull request, or custom build of MicroPython, see the [Custom MicroPython Guide](25_custom_micropython.md) for detailed step-by-step instructions.

## Manual configuration

The manual configuration, including sample configuration files is described in detail in the sister-repo [micropython-stubs][] section [using-the-stubs][]

## using micropython-stubber 

You can install micropython stubber from PyPi using `pip install micropython-stubber`.

## Using micropy-cli

'micropy-cli' is  command line tool for managing MicroPython projects with VSCode
If you want a command line interface to setup a new project and configure the settings as described above for you, then take a look at : [micropy-cli]  

``` 
pip install micropy-cli
micropy init
```

Braden has essentially created a front-end for using micropython-stubber, and the configuration of a project folder for pymakr. 

micropy-cli  maintains its own repository of stubs. 
