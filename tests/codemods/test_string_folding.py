from libcst.codemod import CodemodTest

# MOT
from codemod.commands.constant_folding import ConvertConstantCommand


class TestConvertConstantCommand(CodemodTest):

    # The codemod that will be instantiated for us in assertCodemod.
    TRANSFORM = ConvertConstantCommand

    def test_noop(self) -> None:
        before = """
            foo = "bar"
        """
        after = """
            foo = "bar"
        """

        # Verify that if we don't have a valid string match, we don't make
        # any substitutions.
        self.assertCodemod(before, after, string="baz", constant="BAZ")

    def test_substitution(self) -> None:
        before = """
            def func():
                "bar"
                foo = "bar"
        """
        after = """
            def func():
                BAR
                foo = BAR
        """

        # Verify that if we do have a valid string match, we make a substitution
        self.assertCodemod(before, after, string="bar", constant="BAR")

    def test_substitution2(self) -> None:
        before = """
            foo = "bar"
        """
        after = """
            foo = BAR
        """

        # Verify that if we do have a valid string match, we make a substitution
        self.assertCodemod(before, after, string="bar", constant="BAR")
