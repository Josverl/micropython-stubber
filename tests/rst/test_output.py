# others

# SOT
from rst.output_dict import ModuleSourceDict, ClassSourceDict, FunctionSourceDict


def test_Module_SD():

    od = ModuleSourceDict("utest")
    assert isinstance(od, dict)
    assert isinstance(od["docstr"], list)
    assert isinstance(od["typing"], str)
    assert isinstance(od["version"], str)
    assert isinstance(od["comment"], list)
    assert isinstance(od["constants"], list)


def test_MSD_update():
    od = ModuleSourceDict("utest")
    od.add_constant("YELLOW : Any", True)
    od.add_constant("BLUE : Any", autoindent=True)
    od.add_line("    def fly():")
    od.add_line("         ...")
    out = str(od)
    assert "from typing import" in out
    lines = out.splitlines()
    assert len(lines) >= 8


def test_MSD_var_insert():
    od = ModuleSourceDict("utest")
    def_line = "def fly( color = YELLOW):"
    col_line = "YELLOW : Any"
    od.add_line(def_line)
    od.add_line("     ...")
    # add color later
    od.add_constant(col_line)
    lines = str(od).splitlines()

    l_const = lines.index(col_line)
    l_def = lines.index(def_line)
    assert l_const < l_def, "constants should be placed before functions"


def test_Class_SD():
    NAME = "class bird()"
    cd = ClassSourceDict(NAME)
    assert isinstance(cd, dict)
    assert isinstance(cd["docstr"], list)
    assert isinstance(cd["comment"], list)
    assert isinstance(cd["constants"], list)
    assert isinstance(cd["class"], str)
    assert isinstance(cd["__init__"], list)

    assert cd.name == NAME
    assert cd["docstr"][0] == " " * 4 + '""'


def test_CSD_class():
    # Manually add all
    DOCSTR = '    "class docstring"'
    INIT = "    def __init__(self)->None:"

    cd = ClassSourceDict("class bird()")
    cd.update({"docstr": DOCSTR})
    cd.update({"__init__": [INIT, "    ..."]})

    cd.add_line("    def fly():")
    cd.add_line("         ...")
    cd.add_constant("YELLOW : Any")
    cd.add_constant("BLUE : Any")

    # two constants
    assert len(cd["constants"]) == 2

    lines = str(cd).splitlines()
    assert DOCSTR in lines
    assert INIT in lines


def test_CSD_class_init():
    # start with init
    DOCSTR = ['"class docstring"']
    INIT = "def __init__(self)->None:"

    cd = ClassSourceDict("class bird()", docstr=DOCSTR, init=INIT)

    # cd.add_line("    def fly():")
    # cd.add_line("         ...")
    cd.add_constant("YELLOW : Any")
    cd.add_constant("BLUE : Any")

    lines = str(cd).splitlines()
    # two constants
    assert len(cd["constants"]) == 2
    assert " " * 4 + "BLUE : Any" in lines
    assert " " * 4 + DOCSTR[0] in lines
    assert " " * 4 + INIT in lines
    assert " " * 8 + "..." in lines


def test_FSD_class_init():
    # Function
    DOCSTR = ['"my docstring"']
    DEFN = "def foo()->None:"

    fd = FunctionSourceDict("class bird()", definition=[DEFN], docstr=DOCSTR)
    lines = str(fd).splitlines()
    assert DEFN in lines
    assert " " * 4 + DOCSTR[0] in lines
    assert " " * 4 + "..." in lines
    assert "..." in lines[-1]

    # init with decorator
    fd = FunctionSourceDict(
        "class bird()", definition=[DEFN], docstr=DOCSTR, decorators=["@classmethod"]
    )
    lines = str(fd).splitlines()
    assert "@classmethod" == lines[0]
    assert DEFN in lines
    assert " " * 4 + DOCSTR[0] in lines
    assert " " * 4 + "..." in lines
    assert "..." in lines[-1]


def test_CSD_indent():
    cd = ClassSourceDict("class bird()")
    BLUE = "BLUE : Any"
    GREEN = "GREEN : Any"
    cd.add_constant(BLUE, autoindent=True)
    cd.add_constant(GREEN, autoindent=False)
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
    # od.add(cd)
    od += cd

    cd = ClassSourceDict("class Bar():")
    cd.update({"docstr": '    "Bar docstring"'})
    cd.update({"__init__": ["    def __init__(self)->None:", "    ..."]})

    cd.add_line("    def spam():")
    cd.add_line("         ...")
    od += cd
    l = len(od)
    od.sort()
    assert len(od) == l, "length of the output dictionary should not change by sorting"

    lines = str(od).splitlines()

    l_foo = lines.index("class Foo(Bar):")
    l_bar = lines.index("class Bar():")

    assert l_foo != 0
    assert l_bar != 0

    assert l_foo > l_bar, "Subclass should not be before superclass"


def test_add_class_simple():
    od = ModuleSourceDict("utest")
    # add child class first
    class_1 = ClassSourceDict(
        name="class Foo(Bar):",
        docstr=['"Foo docstring"'],
        init="def __init__(self)->None:",
    )

    method = FunctionSourceDict(
        name="def spam",
        indent=class_1._indent + 4,
        definition=["def spam(foo:int, bar:str)->None:"],
        docstr=['"Spam docstring"'],
    )
    class_1 += method

    od += class_1
    # then add parent
    class_2 = ClassSourceDict(
        name="class Bar():",
        docstr=['"Bar docstring"'],
        init="def __init__(self, parrot)->None:",
    )

    method = FunctionSourceDict(
        name="def parrot",
        indent=class_1._indent + 4,
        definition=["def parrot(foo:int, bar:str)->None:"],
        docstr=['"Parrot docstring"'],
    )

    class_2 += method
    od += class_2
    # ================================
    l = len(od)
    od.sort()
    assert len(od) == l, "length of the output dictionary should not change by sorting"

    lines = str(od).splitlines()

    l_foo = lines.index("class Foo(Bar):")
    l_bar = lines.index("class Bar():")

    assert l_foo != 0
    assert l_bar != 0

    assert l_foo > l_bar, "Subclass should not be before superclass"
