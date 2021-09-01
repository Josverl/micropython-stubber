from typing import OrderedDict, List, Union


class SourceDict(OrderedDict):
    "dict to store ordered source components to be printed as one"

    def __init__(self, base: List, indent: int = 0):
        super().__init__(base)
        self.lf = "\n"  #  add linefeed
        self.indent = indent
        self.nr = 0  # generate incrementing line numbers

    def __str__(self) -> str:
        "convert the OD into a string"
        out = ""
        for item in self.items():
            code = item[1]
            if isinstance(code, str):
                out += code + self.lf
            elif isinstance(code, List):
                for l in code:
                    out += l + self.lf
            else:
                out += str(code)
        return out

    def add_constant(self, line: str, indent: bool = False):
        if indent:
            line = " " * self.indent + line
        "add constant to the constant scope of this block"
        self.update({"constants": self["constants"] + [line]})

    def add_line(self, line: str, indent: bool = False):
        self.nr += 1
        if indent:
            line = " " * self.indent + line
        id = str(self.nr)
        self.setdefault(id, [])
        self.update({id: self[id] + [line]})
        return id

    def index(self, key: str):
        return list(out_dict.keys()).index(key)


class ModuleSourceDict(SourceDict):
    def __init__(self, name: str, indent=0):
        "set correct order a module definition to allow adding class variables"
        super().__init__(
            [
                ("docstr", '""'),
                ("version", "# Version 0.3"),
                ("comment", [f"# module {name} "]),
                ("typing", "from typing import List"),
                ("constants", []),
            ],
            indent,
        )

    def order(self):
        "make sure all classdefs are in order"
        print(" -=-=- SUB /SUPER CLASS ORDERTING TO BE IMPLEMENTED _+_+_+")
        ...

    def __str__(self):
        self.order()
        return super().__str__()

    def find(self, name: str) -> Union[str, None]:
        "find a classnode based on the classname optionally ignoring the superclass"
        keys = list(self.keys())
        # try full match first
        if name in keys:
            return name
        # is there a partial ? - only match before `(`
        name = name.split("(")[0]
        for k in keys:
            if name == k.split("(")[0]:
                return k
        return None


class ClassSourceDict(SourceDict):
    def __init__(self, name: str, indent: int = 4):
        "set correct order for class definitions to allow adding class variables"
        super().__init__(
            [
                ("comment", []),
                ("class", name),  # includes indentation
                ("docstr", '""'),
                ("constants", []),
                ("__init__", []),
            ],
            indent,
        )

        self.lf = "\n"


out_dict = ModuleSourceDict("utest")

out_dict.update({"class bar(foo)": ["class bar(foo):", "   ..."]})
out_dict.update({"class foo": ["class foo:", "   ..."]})

cd = ClassSourceDict("class bird()")
cd.update({"docstr": '    "class docstring"'})
cd.update({"__init__": ["    def __init__(self)->None:", "    ..."]})

cd.add_constant("YELLOW : Any", True)
cd.add_constant("BLUE : Any", indent=True)
cd.add_line("    def fly():")
cd.add_line("         ...")
out_dict.update({"class bird": cd})

for i in range(10, 20):
    out_dict.add_constant(f"parrot_{i} : Any")

if out_dict.index("class bar(foo)") < out_dict.index("class foo"):
    out_dict.move_to_end("class bar(foo)")

print(out_dict)
