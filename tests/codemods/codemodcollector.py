import ast
import os
from pathlib import Path
from typing import Any, List, NamedTuple, Tuple

import pytest

pytestmark = [pytest.mark.stubber, pytest.mark.codemod]

class TestCase(NamedTuple):
    before: str  # The source code before the transformation.
    expected: str  # The source code after the transformation.
    doc_stub: str  # The stub to apply
    stub_file: str  # The path to stub file to apply
    output: Path = None  # where to save the output for testing the tests
    path: Path = None  # where are the tests


def collect_test_cases() -> List[Tuple[Any, ...]]:
    """
    Collect tests cases for the test case folder , each containing a
    - before.py||.pyi
    - after.py||.pyi
    - stub.py||.pyi
    """
    root_test_cases_directory = Path(__file__).parent.joinpath("codemod_test_cases")
    print(root_test_cases_directory)

    test_cases: List = []
    for test_case_directory in root_test_cases_directory.iterdir():
        before_files = list(test_case_directory.glob("before.py")) + list(
            test_case_directory.glob("before.pyi")
        )
        after_files = list(test_case_directory.glob("expected.py")) + list(
            test_case_directory.glob("expected.pyi")
        )
        doc_stubs = list(test_case_directory.glob("doc_stub.py")) + list(
            test_case_directory.glob("doc_stub.pyi")
        )
        if len(before_files) != 1 or len(after_files) != 1 or len(doc_stubs) != 1:
            print("Incorrect test file layout in folder", test_case_directory)
            continue
        # read the test files and add them to the test cases
        with open(before_files[0], encoding="utf-8") as file:
            before = file.read()
        with open(after_files[0], encoding="utf-8") as file:
            expected = file.read()
        with open(doc_stubs[0], encoding="utf-8") as file:
            doc_stub = file.read()

        output = test_case_directory.joinpath("output.py")

        test_cases.append(
            pytest.param(
                TestCase(
                    path=test_case_directory,
                    before=before,
                    doc_stub=doc_stub,
                    expected=expected,
                    stub_file=doc_stubs[0],
                    output=output,
                ),
                id=test_case_directory.name,
            )
        )
    return tuple(test_cases)


# class ExceptionCase(NamedTuple):
#     source: str
#     expected_error_message: str


# def collect_exception_cases() -> Tuple[Any, ...]:
#     root_exception_cases_directory = os.path.join(
#         os.path.dirname(__file__), "exception_cases"
#     )

#     # all .py files in the top-levl of exception cases directory
#     python_files = [
#         os.path.join(root_exception_cases_directory, file)
#         for file in os.listdir(root_exception_cases_directory)
#         if file[-3:] == ".py"
#     ]

#     exception_cases: List = []
#     for python_filename in python_files:
#         with open(python_filename) as python_file:
#             source = python_file.read()

#         # the module's docstring is the expected error message
#         ast_tree = ast.parse(source)
#         docstring = ast.get_docstring(ast_tree)
#         expected_error_message = docstring.replace("\n", " ")

#         test_case_name = os.path.basename(python_filename).replace("_", " ")

#         exception_cases.append(
#             pytest.param(
#                 ExceptionCase(
#                     source=source, expected_error_message=expected_error_message
#                 ),
#                 id=test_case_name,
#             )
#         )

#     return tuple(exception_cases)

# Just for debugging purposes.
if __name__ == "__main__":
    collect_test_cases()
