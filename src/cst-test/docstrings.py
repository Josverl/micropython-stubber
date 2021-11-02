# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# relative import Only needed if LibCTS module is not installed 
# import sys
# sys.path.append("../../")

from typing import List, Tuple, Dict, Optional, Pattern, Sequence, Union
import libcst as cst
from libcst import SimpleStatementLine, BaseCompoundStatement, BaseSuite, Expr, SimpleString, ConcatenatedString



class TypingCollector(cst.CSTVisitor):
    def __init__(self):
        # stack for storing the canonical name of the current function
        self.stack: List[Tuple[str, ...]] = []
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            Tuple[cst.Parameters, Optional[cst.Annotation], Optional[str]],  # value: (params, returns, docstring)
        ] = {}

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        docstring = node.get_docstring(clean=False)
        ##todo: or possible use deep_clone op copy tree 
        # classDef>body>identedblock>body>SimpleStatementLine>SimpleString
        bases = node.bases
        self.annotations[tuple(self.stack)] = (bases, None, docstring)

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self.stack.pop()

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        docstring = node.get_docstring(clean=False)
        self.annotations[tuple(self.stack)] = (node.params, node.returns, docstring)
        return (
            False
        )  # pyi files don't support inner functions, return False to stop the traversal.

    def leave_FunctionDef(self, node: cst.FunctionDef) -> None:
        self.stack.pop()


class TypingTransformer(cst.CSTTransformer):
    def __init__(self, annotations):
        # stack for storing the canonical name of the current function
        self.stack: List[Tuple[str, ...]] = []
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            Tuple[cst.Parameters, Optional[cst.Annotation], Optional[str]],  # value: (params, returns, docstring)
        ] = annotations

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.stack.append(node.name.value)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.CSTNode:
        key = tuple(self.stack)
        self.stack.pop()
        if key in self.annotations:
            annotations = self.annotations[key]
            # Todo: P1 add/update docstring
            print(original_node.body.body[0].body[0].value.value)
            docstring = cst.SimpleString('""" docstring """')
            return updated_node.with_changes(
                # add/update base class(es)
                bases=annotations[0]
            )
            # Todo: add/update decorators

        return updated_node

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        return (
            False
        )  # pyi files don't support inner functions, return False to stop the traversal.

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.CSTNode:
        key = tuple(self.stack)
        self.stack.pop()

        if key in self.annotations:
            annotations = self.annotations[key]
            # Todo: add/update Docstring 
            return updated_node.with_changes(
                params=annotations[0], returns=annotations[1]
            )
        return updated_node
        # .ApplyTypeAnnotationsVisitor
        # See https://libcst.readthedocs.io/en/latest/codemods.html#libcst.codemod.visitors.ApplyTypeAnnotationsVisitor

        # more precise example in :  _apply_type_annotations
        # https://libcst.readthedocs.io/en/latest/_modules/libcst/codemod/visitors/_apply_type_annotations.html#ApplyTypeAnnotationsVisitor
        # # Only add new annotation if explicitly told to overwrite existing
        # # annotations or if one doesn't already exist.
        # if self.overwrite_existing_annotations or not updated_node.returns:
        #     updated_node = updated_node.with_changes(
        #         returns=function_annotation.returns
        #     )
        # # Don't override default values when annotating functions
        # new_parameters = self._update_parameters(function_annotation, updated_node)
        # return updated_node.with_changes(params=new_parameters)



def set_docstring_impl(
    body: Union[BaseSuite, Sequence[Union[SimpleStatementLine, BaseCompoundStatement]]],
    docstring: str,
) -> Optional[bool]:
    """
    Implementation Reference:
    - :func:`ast.get_docstring` https://docs.python.org/3/library/ast.html#ast.get_docstring
    and https://github.com/python/cpython/blob/89aa4694fc8c6d190325ef8ed6ce6a6b8efb3e50/Lib/ast.py#L254
    - PEP 257 https://www.python.org/dev/peps/pep-0257/
    """
    if isinstance(body, Sequence):
        if body:
            expr = body[0]
        else:
            # fixme: what to do if there is no body
            return None
    else:
        expr = body
    while isinstance(expr, (BaseSuite, SimpleStatementLine)):
        if len(expr.body) == 0:
            # fixme: what to do if there is no body
            return None
        expr = expr.body[0]
    if not isinstance(expr, Expr):
        # fixme: what to do if there is no Expression in the body
        return None
    # TODO: Replace the value 
    val = expr.value
    if isinstance(val, (SimpleString, ConcatenatedString)):
        evaluated_value = val.evaluated_value
    else:
        return None

    return evaluated_value

# List methods in ClassDef  list(c.name.value for c in original_node.body.children[2:])

# %%
py_source = '''
"""
Module: 'machine' on micropython-esp32-1.15
"""
# MCU: {'ver': '1.15', 'port': 'esp32', 'arch': 'xtensawin', 'sysname': 'esp32', 'release': '1.15.0', 'name': 'micropython', 'mpy': 10757, 'version': '1.15.0', 'machine': 'ESP32 module (spiram) with ESP32', 'build': '', 'nodename': 'esp32', 'platform': 'esp32', 'family': 'micropython'}
# Stubber: 1.3.11
from typing import Any

class Signal:
    ''
    def __init__(self):
        pass

    def off(self) -> Any:
        pass

    def on(self) -> Any:
        pass

    def value(self) -> Any:
        pass

def time_pulse_us() -> Any:
    pass

def unique_id() -> Any:
    pass

def wake_reason() -> Any:
    pass
'''
pyi_source = '''
def time_pulse_us(pin:Pin, pulse_level:int, timeout_us:int=1000000, /) -> int:
    """
    Time a pulse on the given *pin*, and return the duration of the pulse in
    microseconds.  The *pulse_level* argument should be 0 to time a low pulse
    or 1 to time a high pulse.

    If the current input value of the pin is different to *pulse_level*,
    the function first (*) waits until the pin input becomes equal to *pulse_level*,
    then (**) times the duration that the pin is equal to *pulse_level*.
    If the pin is already equal to *pulse_level* then timing starts straight away.

    The function will return -2 if there was timeout waiting for condition marked
    (*) above, and -1 if there was timeout during the main measurement, marked (**)
    above. The timeout is the same for both cases and given by *timeout_us* (which
    is in microseconds).
    """
    ...


class Signal(Pin):
    """The Signal class is a simple extension of the Pin class. Unlike Pin, which can be only in “absolute” 
    0 and 1 states, a Signal can be in “asserted” (on) or “deasserted” (off) states, while being inverted (active-low) or not. 
    In other words, it adds logical inversion support to Pin functionality. While this may seem a simple addition, it is exactly what 
    is needed to support wide array of simple digital devices in a way portable across different boards, which is one of the major 
    MicroPython goals. Regardless of whether different users have an active-high or active-low LED, a normally open or normally closed 
    relay - you can develop a single, nicely looking application which works with each of them, and capture hardware configuration 
    differences in few lines in the config file of your app.

    """
    def __init__(self, pin_obj:Pin, *,invert:bool=False):
        """ Create a Signal object. There’re two ways to create it:
        By wrapping existing Pin object - universal method which works for any board.
        By passing required Pin parameters directly to Signal constructor, skipping the need to create intermediate Pin object. Available on many, but not all boards.
        The arguments are:
        pin_obj is existing Pin object.
        pin_arguments are the same arguments as can be passed to Pin constructor.
        invert - if True, the signal will be inverted (active low).
        """
        pass


    def off(self) -> None:
        """ Activate signal.
        """
        pass


    def on(self) -> None:
        """ Deactivate signal.
        """
        pass

    def value(self) -> None:
        """ This method allows to set and get the value of the signal, depending on whether the argument x is supplied or not.
            If the argument is omitted then this method gets the signal level, 1 meaning signal is asserted (active) and 0 - signal inactive.
            If the argument is supplied then this method sets the signal level. The argument x can be anything that converts to a boolean. 
            If it converts to True, the signal is active, otherwise it is inactive.
            Correspondence between signal being active and actual logic level on the underlying pin depends on whether signal is inverted (active-low) or not. 
            For non-inverted signal, active status corresponds to logical 1, inactive - to logical 0. For inverted/active-low signal, active status corresponds to logical 0, 
            while inactive - to logical 1.
        """
        pass
'''


# %%
source_tree = cst.parse_module(py_source)
stub_tree = cst.parse_module(pyi_source)


# %%
visitor = TypingCollector()
stub_tree.visit(visitor)

# %%
transformer = TypingTransformer(visitor.annotations)
modified_tree = source_tree.visit(transformer)


# %%
print('='*20)
print(modified_tree.code)


# %%
# Use difflib to show the changes to verify type annotations were added as expected.
import difflib

print(
    "".join(
        difflib.unified_diff(py_source.splitlines(True), modified_tree.code.splitlines(True))
    )
)


# %%
if not modified_tree.deep_equals(source_tree):
    ...  # write to file


