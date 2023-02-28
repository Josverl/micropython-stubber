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

