how to add : 
``` bash
git submodule add --force -b master https://github.com/micropython/micropython.git 
git submodule add --force -b master https://github.com/micropython/micropython-lib.git 
```

how to re-configure existing submodules:
```
git config -f .gitmodules submodule.micropython.branch master
git config -f .gitmodules submodule.micropython-lib.branch master
`` 

how to clone : 
``` bash
git submodule init
git submodule update
```

```
git submodule status --recursive


```