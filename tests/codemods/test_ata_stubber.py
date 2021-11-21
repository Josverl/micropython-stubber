# Copyright (c) 2016-present, Facebook, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

import sys
import textwrap
import unittest
from typing import Type

from libcst import parse_module
from libcst.codemod import Codemod, CodemodContext, CodemodTest
from codemod.visitors import ApplyStubberAnnotationsVisitor
from libcst.testing.utils import data_provider

PYTHON_GRAMMER = "3.8"

TEST_DATA = (
    # base test, update return type
    (
        """
            def foo() -> int: ...
            """,
        """
            def foo():
                return 1
            """,
        """
            def foo() -> int:
                return 1
            """,
    ),
    ## Update parameter and return types with matching params
    (
        """
        def fully_annotated_with_different_stub(a: bool, b: bool) -> str: ...
        """,
        """
        def fully_annotated_with_different_stub(a: int, b: str) -> bool:
            return 'hello'
        """,
        """
        def fully_annotated_with_different_stub(a: bool, b: bool) -> str:
            return 'hello'
        """,
    ),
    # base mpy test - stub update test
    (
        '''
            def unique_id() -> bytes:
                """Returns a byte string with a unique identifier of a board/SoC. It will vary
                from a board/SoC instance to another, if underlying hardware allows. Length
                varies by hardware (so use substring of a full value if you expect a short
                ID). In some MicroPython ports, ID corresponds to the network MAC address.
                """
                ...
        ''',
        """
            def unique_id():
                pass
        """,
        """
            def unique_id() -> bytes:
                pass
        """,
    ),
    # update only existing class functions
    (
        '''
            class WDT:
                """"""
                def __init__(self, timeout :int=2000) -> None:
                    ...
                def feed() -> None:
                    ...
        ''',
        """
            class WDT:
                ''
                def feed():
                    pass

        """,
        """
            class WDT:
                ''
                def feed() -> None:
                    pass
        """,
    ),
    # Does not change docstrings
    (
        '''
            class WDT:
                """RICH Class Docstring"""
                def __init__(self, timeout :int=2000) -> None:
                    ...
                def feed() -> None:
                    "Rich Method Docstring"
                    ...
        ''',
        """
            class WDT:
                'class docstring'
                def feed():
                    'method docstring'
                    pass

        """,
        """
            class WDT:
                'class docstring'
                def feed() -> None:
                    'method docstring'
                    pass
        """,
    ),
)


class TestApplyAnnotationsVisitor(CodemodTest):
    TRANSFORM: Type[Codemod] = ApplyStubberAnnotationsVisitor

    @data_provider(TEST_DATA)
    def test_annotate_functions(self, stub: str, before: str, after: str) -> None:
        context = CodemodContext()
        ApplyStubberAnnotationsVisitor.store_stub_in_context(
            context,
            stub=parse_module(textwrap.dedent(stub.rstrip())),
            overwrite_existing_annotations=True,
        )
        self.assertCodemod(
            before,
            after,
            context_override=context,
            python_version=PYTHON_GRAMMER,
        )

    @data_provider(
        (
            (
                """
                def fully_annotated_with_different_stub(a: bool, b: bool) -> str: ...
                """,
                """
                def fully_annotated_with_different_stub(a: int, b: str) -> bool:
                    return 'hello'
                """,
                """
                def fully_annotated_with_different_stub(a: bool, b: bool) -> str:
                    return 'hello'
                """,
            ),
        )
    )
    def test_annotate_functions_with_existing_annotations(self, stub: str, before: str, after: str) -> None:
        context = CodemodContext()
        ApplyStubberAnnotationsVisitor.store_stub_in_context(
            context,
            parse_module(textwrap.dedent(stub.rstrip())),
        )
        # Test setting the overwrite flag on the codemod instance.
        self.assertCodemod(
            before,
            after,
            context_override=context,
            overwrite_existing_annotations=True,
            python_version=PYTHON_GRAMMER,
        )

        # Test setting the flag when storing the stub in the context.
        context = CodemodContext()
        ApplyStubberAnnotationsVisitor.store_stub_in_context(
            context,
            parse_module(textwrap.dedent(stub.rstrip())),
            overwrite_existing_annotations=True,
        )
        self.assertCodemod(
            before,
            after,
            context_override=context,
            python_version=PYTHON_GRAMMER,
        )

    @data_provider(
        (
            # Does not Add missing Params
            (
                """
                def fully_annotated(a: bool, b: bool) -> str: ...
                """,
                """
                def fully_annotated():
                    return 'hello'
                """,
                """
                def fully_annotated(a: bool, b: bool) -> str:
                    return 'hello'
                """,
            ),
            # does not complete methods parameters
            (
                """
                    class Pin:
                        def __init__( self, id, mode: int = -1, pull: int = -1, value: int = -1, drive=-1, alt=-1 ) -> None:
                            ...
                        def init( self, id, mode: int = -1, pull: int = -1, value: int = -1, drive=-1, alt=-1 ) -> None:
                            ...
                        def irq(self, *argc) -> None:
                            ...
                """,
                """
                    class Pin:
                        def __init__(self):
                            pass

                        def init(self):
                            pass

                        def irq(self):
                            'docstring'
                            pass
                """,
                # TODO: does not update the paramsfor __init__
                """
                    class Pin:
                        def __init__(self, id, mode: int = -1, pull: int = -1, value: int = -1, drive=-1, alt=-1 ) -> None:
                            pass

                        def init(self, id, mode: int = -1, pull: int = -1, value: int = -1, drive=-1, alt=-1 ) -> None:
                            pass

                        def irq(self, *argc) -> None:
                            'docstring'
                            pass
                """,
            ),
        )
    )
    def test_ata_add_missing_params(self, stub: str, before: str, after: str) -> None:
        context = CodemodContext()
        ApplyStubberAnnotationsVisitor.store_stub_in_context(
            context=context,
            stub=parse_module(textwrap.dedent(stub.rstrip())),
            overwrite_existing_annotations=True,
        )
        # Test setting the overwrite flag on the codemod instance.
        self.assertCodemod(
            before,
            after,
            context_override=context,
            overwrite_existing_annotations=True,
            python_version=PYTHON_GRAMMER,
        )
