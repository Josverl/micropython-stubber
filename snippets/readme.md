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

Below is a relevant section from pypy's testing readme.md### How the tests work

The code in this directory is not intended to be directly executed. Instead,
type checkers are run on the code, to check that typing errors are
emitted at the correct places.

Some files in this directory simply contain samples of idiomatic Python, which
should not (if the stubs are correct) cause a type checker to emit any errors.

Many test cases also make use of
[`assert_type`](https://docs.python.org/3.11/library/typing.html#typing.assert_type),
a function which allows us to test whether a type checker's inferred type of an
expression is what we'd like it be.

Finally, some tests make use of `# type: ignore` comments (in combination with
mypy's
[`--warn-unused-ignores`](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-warn-unused-ignores)
setting and pyright's
[`reportUnnecessaryTypeIgnoreComment`](https://github.com/microsoft/pyright/blob/main/docs/configuration.md#type-check-diagnostics-settings)
setting) to test instances where a type checker *should* emit some kind of
error, if the stubs are correct. Both settings are enabled by default for the entire
subdirectory.

For more information on using `assert_type` and
`--warn-unused-ignores`/`reportUnnecessaryTypeIgnoreComment` to test type
annotations,
[this page](https://typing.readthedocs.io/en/latest/source/quality.html#testing-using-assert-type-and-warn-unused-ignores)
provides a useful guide.

### Naming convention

Use the same top-level name for the module / package you would like to test.
Use the `check_${thing}.py` naming pattern for individual test files.

By default, test cases go into a file with the same name as the stub file, prefixed with `check_`.
For example: `stdlib/check_contextlib.py`.

If that file becomes too big, we instead create a directory with files named after individual objects being tested.
For example: `stdlib/builtins/check_dict.py`.