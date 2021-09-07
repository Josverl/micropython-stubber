"""
ModuleSourceDict represents a source file with the following components 
    - docstr
    - version
    - comment
    - typing
    - Optional: list of constants
    - optional: ClassSourcedicts 
    - optional: FunctionSourcedicts 
    - optional: individual lines of code 

ClassSourceDict represents a source file with the following components 
    - comment
    - class
    - docstr
    - Optional: list of constants
    - __init__ : class signature 
    - optional: FunctionSourcedicts 
    - optional: individual lines of code 

FunctionSourceDict represents a source file with the following components 
    - # comments - todo
    - optional: decorator
    - def - function definition 
    - docstr
    - constants
    - body - ...
    - optional: individual lines of code 

SourceDict is the 'base class' 
it 
"""
from __future__ import annotations
from typing import OrderedDict, List, Union
from .classsort import sort_classes


class SourceDict(OrderedDict):
    "(abstract) dict to store source components respecting parent child dependencies and proper definition order"

    def __init__(self, base: List, indent: int = 0, body: int = 0, lf: str = "\n"):
        super().__init__(base)
        self.lf = lf  #  add linefeed
        self._indent = indent  # current base indent
        self._body = body  # for source body is level
        self._nr = 0  # generate incrementing line numbers
        self.name = ""

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

    def __add__(self, dict: SourceDict):
        self.update({dict.name: dict})
        return self

    def add_constant(self, line: str, autoindent: bool = True):
        "add constant to the constant scope of this block"
        if autoindent:
            line = " " * (self._indent + self._body) + line
        self.update({"constants": self["constants"] + [line]})

    def add_line(self, line: str, autoindent: bool = True):
        self._nr += 1
        if autoindent:
            line = " " * (self._indent + self._body) + line
        id = str(self._nr)
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
            body=0,
            lf=lf,
        )
        self.name = name

    def sort(self):
        "make sure all classdefs are in order"
        # new empty one
        new = ModuleSourceDict(self.name, self._indent, self.lf)
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
        # then the classes, already sorted in parent-child order
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
    def __init__(
        self,
        name: str,
        *,
        docstr: str = '""',
        init: str = "def __init__(self)->None:",
        indent: int = 0,
        lf="\n",
    ):
        "set correct order for class definitions to allow adding class variables"
        # add indent
        _docstr = " " * (indent + 4) + docstr
        _init = [" " * (indent + 4) + init]
        # add ...
        _init.append(" " * (indent + 4 + 4) + "...")
        super().__init__(
            [
                ("comment", []),
                ("class", " " * indent + name),  # includes indentation
                ("docstr", _docstr),
                ("constants", []),
                ("__init__", _init),
            ],
            indent,
            body=4,  # class body  indent +4
            lf=lf,
        )
        self.name = name
        self.lf = "\n"


class FunctionSourceDict(SourceDict):
    def __init__(
        self,
        name: str,
        *,
        definition: List[str] = [],
        docstr: str = '""',
        indent: int = 0,
        decorators=[],
        lf="\n",
    ):
        "set correct order for function and method definitions"
        # add indent
        _def = [" " * indent + l for l in definition]
        # indent +4
        _docstr = " " * (indent + 4) + docstr
        # add ...
        super().__init__(
            [
                ("decorator", decorators),
                ("def", _def),  # includes indentation
                ("docstr", _docstr),
                #                ("comments", []),
                ("constants", []),
                ("body", " " * (indent + 4) + "..."),
            ],
            indent,
            body=4,  # function body indent +4
            lf=lf,
        )
        self.name = name
        self.lf = "\n"
