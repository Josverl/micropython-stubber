import pytest

#
from libcst.codemod import CodemodTest
from codemod.commands.noop import NOOPCommand

################################################################################
# Define a few codeblock for testing of the libcst parser
################################################################################

basic = """
    # Basic 
    foo = "" 

    class Class:
        pass

    def foo(a: Class, **kwargs: str) -> Class:
        t= Class()  # This is a comment
        bar = ""
        return t

    bar = Class()
    foo(bar, baz="bla")
"""

positional = """
    # Positional /

    def positional(a, b, /, c:int=None, d=None) -> int:
        print( f"a={a}, b={b} ,c={c} ,d={d}")
        return c
"""

keywords = """
    # Keywords * 
    def keywords(a, b, *, e=42, f=False):
        print(f"a={a}, b={b} ,e={e} ,f={f}")
"""

both = """
    # both keywords and positional
    def both(a, b, /, c:int=None, d=None, *, e=42, f=False):
        print(f"a={a}, b={b} ,e={e} ,f={f}")
"""
################################################################################
# libCtS testing is based on unittest, use this class but call it from pytest
################################################################################
class TestNOOPCodemod(CodemodTest):
    TRANSFORM = NOOPCommand

    def tst_noop_36(self, before, after, version) -> None:
        "Python 3.6 and newer"
        self.assertCodemod(before, after, python_version=version)


################################################################################
# test the support for the Micropython annotation syntax
# Pytest test matrix
################################################################################
@pytest.mark.parametrize(
    "before, after",
    [
        (basic, basic),
        (keywords, keywords),
        (positional, positional),
        (both, both),
    ],
    ids=lambda t: str(t).split()[1],  # use 1st comment as test ID
)
@pytest.mark.parametrize(
    "version",
    [("3.8"), ("3.7"), ("3.5")],
)
def test_LibCST_noop_codemod(version, before, after) -> None:
    # wrap unittest in Pytest for simpler matrix testing
    # known failures
    if "keywords" in before and version < "3.7":
        pytest.skip("STAR param not supported on older python < 3.7")

    if "positional" in before and version < "3.8":
        pytest.skip("SLASH param not supported on older python < 3.8")

    Sot = TestNOOPCodemod()
    Sot.tst_noop_36(before, before, version)
