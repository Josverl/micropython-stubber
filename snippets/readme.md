# Validation Snippets

This folder contains a collection of code snippets to help validate the quality of the stubs by providing some code to validate.

please read : https://typing.readthedocs.io/en/latest/source/quality.html#testing-using-assert-type-and-warn-unused-ignores

## Usage

Note: In order to get the correct typechecking for each of the folders/mcu architectures,  
you should open/add this folder to a VSCode workspace workspace or open it in a seperate VSCode window

You can update / install the type-stubs in the various typings folders by running the following command:

```powershell
# Update the type stubs
stubber switch latest
stubber get-docstubs 
stubber merge --version latest
stubber build --version latest
.\snippets\install-stubs.ps1
```
## Test with pyright (used by the Pylance VSCode extension)

```powershell	
.\snippets\check-stubs.ps1
```

