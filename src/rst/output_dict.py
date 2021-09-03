import re
from typing import OrderedDict, List, Union
from .classsort import sort_classes


class SourceDict(OrderedDict):
    "dict to store source components respecting parent child dependencies and proper definition order"

    def __init__(self, base: List, indent: int = 0, lf: str = "\n"):
        super().__init__(base)
        self.lf = lf  #  add linefeed
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
        return list(self.keys()).index(key)


class ModuleSourceDict(SourceDict):
    def __init__(self, name: str, indent=0, lf: str = "\n"):
        "set correct order a module definition to allow adding class variables"
        super().__init__(
            [
                ("docstr", '""'),
                ("version", ""),
                ("comment", [f"# module {name} "]),
                ("typing", "from typing import List"),
                ("constants", []),
            ],
            indent,
            lf,
        )
        self.name = name

    def sort(self):
        "make sure all classdefs are in order"
        # new empty one
        new = ModuleSourceDict(self.name, self.indent, self.lf)
        # add the standard stuff using a dict comprehension
        new.update(
            {
                k: v
                for (k, v) in self.items()
                if k
                in [
                    "docstr",
                    "version",
                    "comment",
                    "typing",
                    "constants",
                ]
            }
        )
        # then the classes ( if any)
        # TODO: SubClass / Superclass
        for classname in self.classes():
            new.update({classname: self[classname]})
        # then the functions and other
        new.update({k: v for (k, v) in self.items() if k.isdecimal()})
        # now clear and update with new order
        self.clear()
        self.update(new)

    def __str__(self):
        self.sort()
        return super().__str__()

    def find(self, name: str) -> Union[str, None]:
        "find a classnode based on the name with or without the superclass"
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

    def classes(self):
        "get a list of the class names in parent-child order"
        classes = [k for k in self.keys() if isinstance(self[k], ClassSourceDict)]
        # return sorted list
        return sort_classes(classes)


class ClassSourceDict(SourceDict):
    def __init__(self, name: str, indent: int = 4, lf="\n"):
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
            lf,
        )
        self.name = name
        self.lf = "\n"
