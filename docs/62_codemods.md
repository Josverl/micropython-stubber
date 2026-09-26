# Codemods

## What are codemods

Codemods are a way to modify the codebase in a way that is not a breaking change. Codemods are built on [LibCST][libcst] and are written in [Python][python].

Simply said codemods allow one to manipulate python sourcecode (.py and .pyi) files in a structured way withouth the complexities and limitations of using regexes.

## Provided codemods 

You can list the codemods that are provided by micopython stubber using the `libcst.tool`'s  `list` command.
``` bash
python -m libcst.tool list
```

 * add_comment.AddComment - Add comment(s) to each file
 * merge_docstub.MergeCommand - Merge the type-rich information from a doc-stub into a firmware stub

(inherited-method-pruning)=
### Inherited method placeholders

During folder enrichment, the merge pipeline builds a module-qualified inheritance index from the matching doc-stub files. This supports parent and child classes in the same file or in separate files, including imported, aliased, and qualified base names.

When a firmware child class contains a generated `*args, **kwargs` method with a weak return type such as `Any` or `Incomplete`, the merger removes that method if an unambiguous ancestor provides a richer, arity-compatible contract. Static type checkers then use normal inheritance to expose the ancestor's parameter and return types instead of the generic child placeholder. This behavior is generic and is not limited to particular classes or method names.

The merger preserves the child declaration when it cannot prove that removal is safe. In particular, it does not remove:

- `__init__` or `__new__` methods
- methods with meaningful child parameters, return types, docstrings, or decorators
- methods documented directly on the child
- methods whose recorded firmware arity conflicts with the ancestor contract
- methods with unresolved parents or ambiguous multiple inheritance

The merger does not copy ancestor signatures into the child. It only removes proven generated shadows so ordinary Python inheritance provides the documented contract.

To run a codemos use the `codemod` command:

``` bash
python -m libcst.tool codemod <codemod.name> arguments ...

```
examples: 
 * `python -m libcst.tool codemod add_comment.AddComment --help`  
   Get help on the add_comment codemod

## add_comment.AddComment codemod

`Addcomment`  is used to add comments to frozen modudels and modules that are copied from other sources in order to clarify their origin.

examples: 
 * `python -m libcst.tool codemod add_comment.AddComment --help`  
   Get help on the add_comment codemod
  
  * `python -m libcst.tool codemod add_comment.AddComment --comment="This is a comment" ./module.py`  
    Add a comment to the module.py file.  
    `--comment` can be specified multple times to add more comment lines.  
    The comment will be added below any existing comments at the top of the file, and will be prefixed with "# " if it is not already present.  
    If the first comment line already exists in the source code, no comments will be added

  * `python -m libcst.tool codemod add_comment.AddComment --include-stubs  --comment="MicroPython 1.18 frozen modules" ./stubs/micropython-v1_18-frozen`  
    Add a comment to all the .py and .pyi files in the frozen module folder.

## How to run a codemode from the commandline


merge_docstub.MergeCommand 

examples: 
 * `python -m libcst.tool codemod merge_docstub.MergeCommand --help`  
   Get help on the add_comment codemod


## Where are codemods used 
- To merge the type-rich information from a doc-stub into a firmware stub

- To create the different variants of `createstubs.py` 
  `stubber make-variants` 
  This will use moding the code to: 
  - a memory efficient version (low memory)
  - a version that allows the MCU to restart without losing the progress ( very low memory)

[libcts]: https://libcst.readthedocs.io/en/latest/index.html

