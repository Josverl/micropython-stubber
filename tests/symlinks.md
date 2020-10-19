

## create symlink on windows 

``` powershell
# requires  Developer enabled or elevated powershell propmpt 
# target must be an absolute path, resolve path is used to resolve the relative path to absolute
New-Item -ItemType SymbolicLink -Path "all-stubs" -Target (Resolve-Path -Path ../micropython-stubs/stubs)

```
