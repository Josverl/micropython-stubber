"""Codemod to add methods to a classes.

Used to add methods that are documented, but are not reported by the firmware, 
so they are also not present in the board stubs.
"""


import libcst as cst
from libcst import matchers as m

# todo: extract the call method from the docstubs
FNDEF_PIN_CALL = '''
def __call__(self, x: Optional[Any] = None) -> Any:
    """
    Pin objects are callable.  The call method provides a (fast) shortcut to set
    and get the value of the pin.  It is equivalent to Pin.value([x]).
    See :meth:`Pin.value` for more details.
    """
    ...
'''

# print(call_meth)


class CallAdder(m.MatcherDecoratableTransformer):
    """Add a __call__ method to a class if it is missing."""
    class_name = "Pin"  # class name 
    has_call = 0 # number of __call__ methods found

    def __init__(self) -> None:
        super().__init__()
        # parse the (default) call method once
        self.call_meth = cst.parse_statement(FNDEF_PIN_CALL)


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
