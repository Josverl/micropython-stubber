# Using stubs
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
