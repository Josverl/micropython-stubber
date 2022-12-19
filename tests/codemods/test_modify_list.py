import pytest
from libcst.codemod import CodemodTest
import libcst as cst
import libcst.matchers as m
from stubber.codemod.modify_list import ListChangeSet, ModifyListElements
from collections import namedtuple
from textwrap import dedent

# mark all tests
pytestmark = pytest.mark.codemod


Case = namedtuple("Case", ["before", "after", "changeset", "scope"], defaults=["", "", None, None])


scenarios = {
    "add_string_element": Case(
        before="""
        a_list = ["foo", "bar"]
        """,
        after="""
        a_list = ["foo", "bar", "foobar"]
        """,
        changeset=ListChangeSet.from_strings(add=["foobar"]),
    ),
    "add_string_element_replace": Case(
        before="""
        a_list = ["foo", "bar"]
        """,
        after="""
        a_list = ["foobar"]
        """,
        changeset=ListChangeSet.from_strings(add=["foobar"], replace=True),
    ),
    "remove_string_element": Case(
        before="""
        a_list = ["foo", "bar"]
        """,
        after="""
        a_list = ["foo"]
        """,
        changeset=ListChangeSet.from_strings(remove=["bar"]),
    ),
    # a technically valid case.
    "remove_string_element_replace": Case(
        before="""
        a_list = ["foo", "bar"]
        """,
        after="""
        a_list = []
        """,
        changeset=ListChangeSet.from_strings(remove=["bar"], replace=True),
    ),
    "add_cst_node": Case(
        before="""
        a = "foo"
        b = "bar"
        c = ("foo", "bar")
        a_list = [a, b]
        """,
        after="""
        a = "foo"
        b = "bar"
        c = ("foo", "bar")
        a_list = [a, b, c]
        """,
        changeset=ListChangeSet(add=[cst.Name("c")]),
    ),
    "remove_cst_node_match": Case(
        before="""
        a = "foo"
        b = "bar"
        c = ("foo", "bar")
        a_list = [a, b, c]
        """,
        after="""
        a = "foo"
        b = "bar"
        c = ("foo", "bar")
        a_list = [a]
        """,
        changeset=ListChangeSet(remove=[m.Name("c"), m.Name("b")]),
    ),
    "add_scoped_string": Case(
        before="""
        a_list = ["other", "values"]
        def main():
            a_list = ["foo", "bar"]
        """,
        after="""
        a_list = ["other", "values"]
        def main():
            a_list = ["foo", "bar", "foobar"]
        """,
        changeset=ListChangeSet.from_strings(add=["foobar"]),
        scope=m.FunctionDef(name=m.Name("main")),
    ),
    "remove_scoped_string": Case(
        before="""
        a_list = ["other", "values"]
        def main():
            a_list = ["foo", "bar"]
        """,
        after="""
        a_list = ["other", "values"]
        def main():
            a_list = ["foo"]
        """,
        changeset=ListChangeSet.from_strings(remove=["bar"]),
        scope=m.FunctionDef(name=m.Name("main")),
    ),
    "handles_unmatched_remove": Case(
        before="""
        a_list = ["other", "values"]
        def main():
            a_list = ["foo", "bar"]
        """,
        after="""
        a_list = ["other", "values"]
        def main():
            a_list = ["foo", "bar"]
        """,
        changeset=ListChangeSet.from_strings(remove=["abc123"]),
        scope=m.FunctionDef(name=m.Name("main")),
    ),
}


class TestModifyListElements:
    before: str
    after: str
    changeset: ListChangeSet
    scope: m.BaseMatcherNode

    @pytest.fixture(params=[pytest.param(v, id=k) for k, v in scenarios.items()], autouse=True)
    def scenario(self, request: pytest.FixtureRequest):
        request.cls.before = dedent(request.param.before)
        request.cls.after = dedent(request.param.after)
        request.cls.changeset = request.param.changeset
        request.cls.scope = request.param.scope

    def test_scenario(self):
        trans = ModifyListElements(change_set=self.changeset, scope_matcher=self.scope)
        module = cst.parse_module(self.before)
        result = module.visit(trans)
        assert result.code == self.after
