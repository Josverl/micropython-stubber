# others

# SOT
from rst.output_dict import ModuleSourceDict, ClassSourceDict


def test_Module_SD():

    od = ModuleSourceDict("utest")
    assert isinstance(od, dict)
    assert isinstance(od["docstr"], str)
    assert isinstance(od["typing"], str)
    assert isinstance(od["version"], str)
    assert isinstance(od["comment"], list)
    assert isinstance(od["constants"], list)


def test_MSD_update():
    od = ModuleSourceDict("utest")
    od.add_constant("YELLOW : Any", True)
    od.add_constant("BLUE : Any", indent=True)
    od.add_line("    def fly():")
    od.add_line("         ...")
    out = str(od)
    assert "from typing import" in out
    lines = out.splitlines()
    assert len(lines) >= 8


def test_MSD_var_insert():
    od = ModuleSourceDict("utest")
    def_line = "    def fly( color = YELLOW):"
    col_line = "YELLOW : Any"
    od.add_line(def_line)
    od.add_line("         ...")
    # add color later
    od.add_constant(col_line, True)
    lines = str(od).splitlines()

    l_const = lines.index(col_line)
    l_def = lines.index(def_line)
    assert l_const < l_def, "constants should be placed before functions"


def test_Class_SD():
    cd = ClassSourceDict("class bird()")
    assert isinstance(cd, dict)
    assert isinstance(cd["docstr"], str)
    assert isinstance(cd["comment"], list)
    assert isinstance(cd["constants"], list)
    assert isinstance(cd["class"], str)
    assert isinstance(cd["__init__"], list)


def test_CSD_class():
    cd = ClassSourceDict("class bird()")
    cd.update({"docstr": '    "class docstring"'})
    cd.update({"__init__": ["    def __init__(self)->None:", "    ..."]})

    cd.add_line("    def fly():")
    cd.add_line("         ...")
    cd.add_constant("YELLOW : Any", True)
    cd.add_constant("BLUE : Any", indent=True)

    lines = str(cd).splitlines()


def test_CSD_indent():
    cd = ClassSourceDict("class bird()")
    BLUE = "BLUE : Any"
    GREEN = "GREEN : Any"
    cd.add_constant(BLUE, indent=True)
    cd.add_constant(GREEN, indent=False)
    lines = str(cd).splitlines()
    # should be indented
    assert " " * 4 + BLUE in lines
    # should NOT be indented
    assert GREEN in lines


def test_add_class():
    od = ModuleSourceDict("utest")

    cd = ClassSourceDict("class Foo(Bar):")
    cd.update({"docstr": '    "Foo docstring"'})
    cd.update({"__init__": ["    def __init__(self)->None:", "    ..."]})

    cd.add_line("    def spam():")
    cd.add_line("         ...")
    od.update({cd.name: cd})

    cd = ClassSourceDict("class Bar():")
    cd.update({"docstr": '    "Bar docstring"'})
    cd.update({"__init__": ["    def __init__(self)->None:", "    ..."]})

    cd.add_line("    def spam():")
    cd.add_line("         ...")
    od.update({cd.name: cd})
    l = len(od)
    od.sort()
    assert len(od) == l, "length of the output dictionary should not change by sorting"

    lines = str(od).splitlines()

    l_foo = lines.index("class Foo(Bar):")
    l_bar = lines.index("class Bar():")

    assert l_foo != 0
    assert l_bar != 0

    assert l_foo > l_bar, "Subclass should not be before superclass"
