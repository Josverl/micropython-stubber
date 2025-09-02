"""Codemod to add methods to a classes.

Used to add methods that are documented, but are not reported by the firmware, 
so they are also not present in the MCU stubs.
"""


from typing import Optional
import libcst as cst
from libcst import matchers as m


# there is no simple way to re-use the code from multiple classes / methods
# but could be added https://stackoverflow.com/questions/17522706/how-to-pass-an-instance-variable-to-a-decorator-inside-class-definition?noredirect=1&lq=1
# so for now, just copy the code, or use a module scoped variable - but that is not thread safe


class CallFinder(m.MatcherDecoratableTransformer):
    """Find the Pin.__call__ method and extract it from a (machine) module."""

    class_name: str = "Pin"  # class name
    method_name: str = "__call__"  # method name

    def __init__(self):
        super().__init__()
        self.call_meth: Optional[cst.FunctionDef] = None

    @m.call_if_inside(m.ClassDef(name=m.Name(class_name)))
    @m.visit(m.FunctionDef(name=m.Name(method_name)))
    def detect_call(self, node: cst.FunctionDef) -> None:
        """find the  __call__ method and store it."""
        self.call_meth = node


class CallAdder(m.MatcherDecoratableTransformer):
    """Add a __call__ method to a class if it is missing."""

    class_name = "Pin"  # class name
    has_call = 0  # number of __call__ methods found

    def __init__(self, call_meth: cst.FunctionDef) -> None:
        super().__init__()
        self.call_meth = call_meth

    @m.call_if_inside(m.ClassDef(name=m.Name(class_name)))
    @m.visit(m.FunctionDef(name=m.Name("__call__")))
    def detect_call(self, node: cst.FunctionDef) -> None:
        """Detect if the class already has a __call__ method."""
        self.has_call += 1

    @m.leave(m.ClassDef(name=m.Name(class_name)))
    def add_call(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        """Add the __call__ method to the class if it is not already there."""
        if self.has_call:
            # no change needed
            return updated_node
        assert isinstance(updated_node.body, cst.IndentedBlock), "Class body is not indented"
        # Add it to the end of the body & keep other body items
        new_body = cst.IndentedBlock(
            body=list(updated_node.body.body) + [self.call_meth],
            header=updated_node.body.header,
            footer=updated_node.body.footer,
            indent=updated_node.body.indent,
        )
        return updated_node.with_changes(body=new_body)
