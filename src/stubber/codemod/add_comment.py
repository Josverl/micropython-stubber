"""Add comment(s) to each file"""
# sourcery skip: snake-case-functions

import argparse
from typing import List
from libcst import Module, Comment
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.helpers.module import insert_header_comments

import re
from typing import Pattern


class AddComment(VisitorBasedCodemodCommand):
    DESCRIPTION: str = "Add comment(s) to each file"

    @staticmethod
    def add_args(arg_parser: argparse.ArgumentParser) -> None:
        """Add command-line args that a user can specify for running this codemod."""
        arg_parser.add_argument(
            "-c",
            "--comment",
            dest="comments",
            action="extend",
            nargs="+",
            metavar="COMMENT",
            help="Comment statement(s) to add to each file",
            type=str,
            required=True,
        )

    def __init__(self, context: CodemodContext, comments: List[str]) -> None:
        """
        Initialize the base class with context, and save our args. Remember, the
        "dest" for each argument we added above must match a parameter name in
        this init.
        """
        super().__init__(context)
        self.comments = [c if c[0] == "#" else f"# {c}" for c in comments]
        # regex only checks for the first line of the comment
        self._regex_pattern: Pattern[str] = re.compile(rf"^{self.comments[0]}\s*$")
        self.needs_add = True

    def visit_Comment(self, node: Comment) -> None:
        """
        connect comments from the source
        """
        if self._regex_pattern.search(node.value):
            self.needs_add = False

    def leave_Module(self, original_node: Module, updated_node: Module) -> Module:
        """If the tag already exists, don't modify the file."""
        return insert_header_comments(updated_node, self.comments) if self.needs_add else updated_node
