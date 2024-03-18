import pytest
from libcst.codemod import CodemodTest
from stubber.codemod.add_comment import AddComment

# mark all tests
pytestmark = [pytest.mark.stubber, pytest.mark.codemod]


class AddCommentTest(CodemodTest):
    "test adding comments"

    TRANSFORM = AddComment  # The codemod that will be instantiated for us in assertCodemod.

    def test_add_one(self) -> None:  # sourcery skip: class-extract-method
        before = """\
            foo = "bar"
        """
        after = """\
            # hello
            foo = "bar"
        """
        self.assertCodemod(before, after, comments=["# hello"])

    def test_add_list(self) -> None:
        before = """\
            foo = "bar"
        """
        after = """\
            # hello
            # dude
            foo = "bar"
        """
        self.assertCodemod(
            before,
            after,
            comments=[
                "hello",
                "# dude",
            ],
        )

    def test_add_nc(self) -> None:
        before = """\
            foo = "bar"
        """
        after = """\
            # hello
            foo = "bar"
        """
        self.assertCodemod(before, after, comments=["hello"])

    # @pytest.mark.skip(reason="not implemented yet")
    def test_add_no_dups(self) -> None:
        before = """\
            # hello
            # foo
            foo = "bar"
        """
        after = """\
            # hello
            # foo
            foo = "bar"
        """
        self.assertCodemod(before, after, comments=["hello"])
