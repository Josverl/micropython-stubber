import argparse
from ast import literal_eval
from typing import Union

import libcst as cst

from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand

# from libcst.codemod.visitors import AddImportsVisitor


# Tutorial https://libcst.readthedocs.io/en/latest/codemods_tutorial.html


class ConvertConstantCommand(VisitorBasedCodemodCommand):

    # Add a description so that future codemodders can see what this does.
    DESCRIPTION: str = "Converts raw strings to constant accesses."

    @staticmethod
    def add_args(arg_parser: argparse.ArgumentParser) -> None:
        # Add command-line args that a user can specify for running this
        # codemod.
        arg_parser.add_argument(
            "--string",
            dest="string",
            metavar="STRING",
            help="String contents that we should look for.",
            type=str,
            required=True,
        )
        arg_parser.add_argument(
            "--constant",
            dest="constant",
            metavar="CONSTANT",
            help="Constant identifier we should replace strings with.",
            type=str,
            required=True,
        )

    def __init__(self, context: CodemodContext, string: str, constant: str) -> None:
        # Initialize the base class with context, and save our args. Remember, the
        # "dest" for each argument we added above must match a parameter name in
        # this init.
        super().__init__(context)
        self.string = string
        self.constant = constant

    def leave_SimpleString(self, original_node: cst.SimpleString, updated_node: cst.SimpleString) -> Union[cst.SimpleString, cst.Name]:
        if literal_eval(updated_node.value) == self.string:

            return cst.Name(self.constant)
        # This isn't a string we're concerned with, so leave it unchanged.
        return updated_node
