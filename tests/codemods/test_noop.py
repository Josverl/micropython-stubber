#
from libcst.codemod import CodemodTest
from src.codemod.commands.noop import NOOPCommand


class TestNOOPCodemod(CodemodTest):
    TRANSFORM = NOOPCommand

    def test_noop_36(self) -> None:
        "Python 3.6 and newer"
        before = """
            foo: str = ""

            class Class:
                pass

            def foo(a: Class, **kwargs: str) -> Class:
                t: Class = Class()  # This is a comment
                bar = ""
                return t

            bar = Class()
            foo(bar, baz="bla")
        """
        after = """
            foo: str = ""

            class Class:
                pass

            def foo(a: Class, **kwargs: str) -> Class:
                t: Class = Class()  # This is a comment
                bar = ""
                return t

            bar = Class()
            foo(bar, baz="bla")
        """

        self.assertCodemod(before, after)
        self.assertCodemod(before, after, python_version="3.6")

    def test_noop_35(self) -> None:
        "Python 3.5 or older code"
        before = """
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
        after = """
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
        self.assertCodemod(before, after, python_version="3.3")
        self.assertCodemod(before, after, python_version="3.5")
