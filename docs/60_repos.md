# Repo structure 

- [This and sister repos](#this-and-sister-repos) 
- [Structure of this repo](#structure-of-this-repo)
- [Naming Convention and Stub folder structure][naming-convention]
- 2 python versions 


## This and sister repos

| repo                | Why                      | Where                    | example
|---------------------|--------------------------|----------------------------------|-----------------------------------|
| micropython-stubber | needed to make stubs     | in your source folder            | develop/micropython-stubber | 
| micropython         | to collect frozen modules| submodule of micropython-stubber | develop/micropython-stubber/micropython
| micropython-lib     | to collect frozen modules| submodule of micropython-stubber | develop/micropython-stubber/micropython-lib
| micropython-stubs   | stores collected stubs   | next to the `stubber`            | develop/micropython-stubs         |

```{note}
- recommended is to create a symlink from `develop/micropython-stubber\all-stubs` to `develop/micropython-stubs`
```
```{note}
- For Git submodules please refer to https://git-scm.com/book/en/v2/Git-Tools-Submodules
```

## Structure of this repo 

The file structure is based on my personal windows environment, but you should be able to adapt that without much hardship to you own preference and OS.

| What                 | Details                      | Where                             |
|----------------------|--------------------------|-----------------------------------|
| stub root            | symlink to connect the 2 sister-repos | all_stubs|
| firmware stubber     | MicroPython              | board/createstubs.py|
| minified firmware stubber | MicroPython         | minified/createstubs.py|
| PC based scripts     | CPython                  | src/*|
| PC based scripts     | CPython                  | process.py|
| pytest tests         |                          | test/*|
|                           |                                       |                         |

## Naming Convention and Stub folder structure

| What                 | Why                      | Where                             |
|----------------------|--------------------------|-----------------------------------|
| stub root            | connect the 2 repos                         | all_stubs|
| cpython stubs for micropython core | adapt for differences between CPython and MicroPython | stubs/cpython-core |
| generated stub files | needed to use stubs      | stubs/{firmware}-{port}-{version}-frozen |
| Frozen stub files    | better code intellisense | stubs/{firmware}-{version}-frozen |


Note: I found that, for me, using submodules caused more problems than it solved. So instead I link the two main repo's using a [symlink][].

***Note:*** I in the repo tests I have used the folders `TESTREPO-micropython`  and `TESTREPO-micropython-lib` to avoid conflicts with any development that you might be doing on similar `micropython` repos at the potential cost of a little disk space.

``` powershell
cd /develop 

git clone  https://github.com/josverl/micropython-stubber.git 
git clone  https://github.com/josverl/micropython-stubs.git 
git clone  https://github.com/micropython/micropython.git 
git clone  https://github.com/micropython/micropython.git 
```


## Create a symbolic link

To create the symbolic link to the `../micropython-stubs/stubs` folder the instructions differ slightly for each OS/
The below examples assume that the micropython-stubs repo is cloned 'next-to' your project folder.
please adjust as needed.

### Windows 10 

Requires `Developer enabled` or elevated powershell prompt.

``` powershell
# target must be an absolute path, resolve path is used to resolve the relative path to absolute
New-Item -ItemType SymbolicLink -Path "all-stubs" -Target (Resolve-Path -Path ../micropython-stubs/stubs)
```

or use [mklink](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/mklink) in an (elevated) command prompt

``` sh
rem target must be an absolute path
mklink /d all-stubs c:\develop\micropython-stubs\stubs
```

### Linux/Unix/Mac OS

``` sh
# target must be an absolute path
ln -s /path/to/micropython-stubs/stubs all-stubs
```


[stubs-repo]:   https://github.com/Josverl/micropython-stubs
[stubs-repo2]:  https://github.com/BradenM/micropy-stubs
[micropython-stubber]: https://github.com/Josverl/micropython-stubber
[micropython-stubs]: https://github.com/Josverl/micropython-stubs#micropython-stubs
[micropy-cli]: https://github.com/BradenM/micropy-cli
[using-the-stubs]: https://github.com/Josverl/micropython-stubs#using-the-stubs
[demo]:         docs/img/demo.gif	"demo of writing code using the stubs"
[stub processing order]: docs/img/stuborder_pylance.png	"recommended stub processing order"
[naming-convention]: #naming-convention-and-stub-folder-structure
[all-stubs]: https://github.com/Josverl/micropython-stubs/blob/main/firmwares.md
[micropython]: https://github.com/micropython/micropython
[micropython-lib]:  https://github.com/micropython/micropython-lib
[pycopy]: https://github.com/pfalcon/pycopy
[pycopy-lib]: https://github.com/pfalcon/pycopy-lib
[createstubs-flow]: docs/img/createstubs-flow.png
[symlink]: #create-a-symbolic-link

