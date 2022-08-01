import pytest
from libcst.codemod._testing import _CodemodTest, CodemodContext, parse_module, CodemodTest, PartialParserConfig
from stubber.codemod.merge_docstub import MergeCommand
from .codemodcollector import (
    TestCase as MyTestCase,
    collect_test_cases,
)
import difflib
from typing import Optional, Sequence, Tuple, Dict
from pathlib import Path


class PytestCodemodTest(_CodemodTest):
    "CodeMod test that uses use _CodemodTest as the superclass as that does not inherit from unittest.TestCase which will break pytest.parametrize"

    def assertEqual(self, first, second, msg=None):
        """basic assertEqual implementation, not type specific."""
        if not first == second:
            raise AssertionError(msg)

    def assertCodemod(
        self,
        before: str,
        after: str,
        *args: object,
        context_override: Optional[CodemodContext] = None,
        python_version: Optional[str] = None,
        expected_warnings: Optional[Sequence[str]] = None,
        expected_skip: bool = False,
        save_output: Optional[Path] = None,
        **kwargs: object,
    ) -> None:
        """
        Given a before and after code string, and any args/kwargs that should
        be passed to the codemod constructor specified in
        :attr:`~CodemodTest.TRANSFORM`, validate that the codemod executes as
        expected. Verify that the codemod completes successfully, unless the
        ``expected_skip`` option is set to ``True``, in which case verify that
        the codemod skips.  Optionally, a :class:`CodemodContext` can be provided.
        If none is specified, a default, empty context is created for you.
        Additionally, the python version for the code parser can be overridden
        to a valid python version string such as `"3.6"`. If none is specified,
        the version of the interpreter running your tests will be used. Also, a
        list of warning strings can be specified and :meth:`~CodemodTest.assertCodemod`
        will verify that the codemod generates those warnings in the order
        specified. If it is left out, warnings are not checked.


        """

        context = context_override if context_override is not None else CodemodContext()
        # pyre-fixme[45]: Cannot instantiate abstract class `Codemod`.
        transform_instance = self.TRANSFORM(context, *args, **kwargs)
        input_tree = parse_module(
            CodemodTest.make_fixture_data(before),
            config=(PartialParserConfig(python_version=python_version) if python_version is not None else PartialParserConfig()),
        )
        try:
            output_tree = transform_instance.transform_module(input_tree)

            if save_output:
                with open(save_output, "w") as file:
                    file.write(output_tree.code)
        except SkipFile:
            if not expected_skip:
                raise
            output_tree = input_tree
        else:
            if expected_skip:
                # pyre-ignore This mixin needs to be used with a UnitTest subclass.
                self.fail("Expected SkipFile but was not raised")

        # pyre-ignore This mixin needs to be used with a UnitTest subclass.
        self.assertEqual(
            CodemodTest.make_fixture_data(after),
            CodemodTest.make_fixture_data(output_tree.code),
        )
        if expected_warnings is not None:
            # pyre-ignore This mixin needs to be used with a UnitTest subclass.
            self.assertSequenceEqual(expected_warnings, context.warnings)


@pytest.mark.parametrize("test_case", collect_test_cases())
class TestMergeDocStubs(PytestCodemodTest):
    # The codemod that will be instantiated for us in assertCodemod.
    TRANSFORM = MergeCommand

    def test_merge_from_docstub(self, test_case: MyTestCase) -> None:
        # context will allows the detection of relative imports
        if "_skip" in str(test_case.path):
            pytest.skip("Skipping test because of _skip")
        if "_xfail" in str(test_case.path):
            pytest.xfail("xfail")
            
        self.assertCodemod(
            test_case.before,
            test_case.after,
            stub_file=test_case.stub_file,
            save_output=test_case.output,
        )
