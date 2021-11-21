""" 
    Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking 
    using a custom-built parser to read and process the micropython RST files
    - generates:
        - modules 
            - docstrings

        - function definitions 
            - function parameters based on documentation
            - docstrings

        classes
            - docstrings
            - __init__ method
            - parameters based on documentation for class 
            - methods
                - parameters based on documentation for the method
                - docstrings

        - exceptions

    - tries to determine the return type by parsing the docstring.
        - Imperative verbs used in docstrings have a strong correlation to return -> None
        - recognizes documented Generators, Iterators, Callable
        - Coroutines are identified based tag "This is a Coroutine". Then if the return type was Foo, it will be transformed to : Coroutine[Foo]
        - a static Lookup list is used for a few methods/functions for which the return type cannot be determined from the docstring. 
        - add NoReturn to a few functions that never return ( stop / deepsleep / reset )
        - if no type can be detected the type `Any` is used

    The generated stub files are formatted using `black` and checked for validity using `pyright`
    Note: black on python 3.7 does not like some function defs 
    `def sizeof(struct, layout_type=NATIVE, /) -> int:` 

    - ordering of inter-dependent classes in the same module   
    
    - Literals / constants
        - documentation contains repeated vars with the same indentation
        - Module level:
        .. code-block:: 

            .. data:: IPPROTO_UDP
                     IPPROTO_TCP

        - class level: 
        .. code-block:: 
        
            .. data:: Pin.IRQ_FALLING
                    Pin.IRQ_RISING
                    Pin.IRQ_LOW_LEVEL
                    Pin.IRQ_HIGH_LEVEL

                    Selects the IRQ trigger type.

        - literals documented using a wildcard are added as comments only 

    - add GLUE imports to allow specific modules to import specific others. 

    - repeats of definitions in the rst file for similar functions or literals
        - CONSTANTS ( module and Class level )
        - functions
        - methods

    - Child/ Parent classes
        are added based on a (manual) lookup table CHILD_PARENT_CLASS



Not yet implemented 
-------------------

    - manual tweaks for uasync 
        https://docs.python.org/3/library/typing.html#asynchronous-programming


    # correct warnings for 'Unsupported escape sequence in string literal'


"""

import sys
import json
import re
import subprocess
import basicgit as git
from typing import List, Tuple
from pathlib import Path
from utils import flat_version

from rst import (
    return_type_from_context,
    TYPING_IMPORT,
    MODULE_GLUE,
    PARAM_FIXES,
    CHILD_PARENT_CLASS,
    ModuleSourceDict,
    ClassSourceDict,
    FunctionSourceDict,
)

NEW_OUTPUT = True
#: self.gather_docs = True
SEPERATOR = "::"


def _color(c, *args) -> str:
    s = str(*args)
    return f"\033[{c}m {s}\033[00m"


def _green(*args) -> str:
    return _color(92, *args)


def _red(*args) -> str:
    return _color(91, *args)


class RSTReader:
    __debug = False  # a
    verbose = True
    gather_docs = False  # used only during Development
    target = ".py"  # py/pyi

    def __init__(self, v_tag="v1.xx"):
        self.line_no: int = 0  # current Linenumber used during parsing.
        self.filename = ""

        self.current_module = ""
        self.current_class = ""
        self.current_function = ""  # function & method

        # input buffer
        self.rst_text: List[str] = []
        self.max_line = 0

        # Output buffer
        self.output: List[str] = []
        self.output_dict: ModuleSourceDict = ModuleSourceDict("")
        self.output_dict.add_import(TYPING_IMPORT)

        self.source_tag = v_tag

        # development aids only
        self.return_info: List[Tuple] = []
        self.last_line = ""

    @property
    def line(self) -> str:
        "get the current line from input, also stores this as last_line to allow for inspection and dumping the json file"
        if self.line_no >= 0 and self.line_no <= self.max_line:
            self.last_line = self.rst_text[self.line_no]
        else:
            self.last_line = ""
        return self.last_line

    @property
    def module_names(self) -> List[str]:
        "list of possible module names [uname , name] (longest first)"
        namelist: List[str] = []
        if self.current_module == "":
            return namelist
        # deal with module names "esp and esp.socket"
        if "." in self.current_module:
            names = [self.current_module, self.current_module.split(".")[0]]
        else:
            names = [self.current_module]
        # process
        for c_mod in names:
            if self.current_module[0] != "u":
                namelist += [f"u{c_mod}", c_mod]
            else:
                namelist += [c_mod, c_mod[1:]]
        return namelist

    def strip_prefixes(self, name: str, strip_mod: bool = True, strip_class: bool = False):
        "Remove the modulename. and or the classname. from the begining of a name"
        if strip_mod:
            prefixes = self.module_names
        else:
            prefixes = []
        if strip_class and self.current_class != "":
            prefixes += [self.current_class]
        for prefix in prefixes:
            if len(prefix) > 1 and prefix + "." in name:
                name = name.replace(prefix + ".", "")
        return name

    def log(self, *arg):
        if self.verbose:
            print(*arg)

    def leave_class(self):
        if self.current_class != "":
            self.current_class = ""

    def read_file(self, filename: Path):
        print(f"::group::[Reading RST] {filename}")
        # ingore Unicode decoding issues
        with open(filename, errors="ignore", encoding="utf8") as file:
            self.rst_text = file.readlines()
        self.filename = filename
        self.max_line = len(self.rst_text) - 1
        self.current_module = filename.stem  # just to be sure

    def prepare_output(self):
        "clean up some trailing spaces and commas"
        if NEW_OUTPUT:
            lines = str(self.output_dict).splitlines(keepends=True)
            self.output = lines
        for i in range(0, len(self.output)):
            if "(self, ) ->" in self.output[i]:
                self.output[i] = self.output[i].replace("(self, ) ->", "(self) ->")

    def write_file(self, filename: Path) -> bool:
        self.prepare_output()
        try:
            print(f" - Writing to: {filename}")
            with open(filename, mode="w", encoding="utf8") as file:
                file.writelines(self.output)
        except OSError as e:
            print(e)
            return False
        if self.gather_docs:
            print(f" - Writing to: {filename}")
            with open(filename.with_suffix(".json"), mode="w", encoding="utf8") as file:
                json.dump(self.return_info, file, ensure_ascii=False, indent=4)
            self.return_info = []

        return True

    def parse_docstring(self) -> List[str]:
        """Read a textblock that will be used as a docstring, or used to process a toc tree
        The textblock is terminated at the following RST line structures/tags

            .. <anchor>
            -- Heading
            == Heading
            ~~ Heading

        The blank lines at the start and end are removed to limit the space the docstring takes up.
        """
        if self.line_no >= len(self.rst_text):
            raise IndexError
        block: List[str] = []
        self.line_no += 1  # advance over current line
        try:
            while (
                self.line_no < len(self.rst_text)
                and not self.rst_text[self.line_no]
                .lstrip()
                .startswith("..")  # stop at anchor ( however .. note: could be considered to be added)
                and not self.rst_text[min(self.line_no + 1, self.max_line - 1)].startswith("--")  # Heading --
                and not self.rst_text[min(self.line_no + 1, self.max_line - 1)].startswith("==")  # Heading ==
                and not self.rst_text[min(self.line_no + 1, self.max_line - 1)].startswith("~~")  # Heading ~~
            ):
                line = self.rst_text[self.line_no]
                block.append(line.rstrip())
                self.line_no += 1  # advance line
        except IndexError:
            pass
        # if a Quoted Literal Block , then remove the first character of each line
        # https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#quoted-literal-blocks
        if len(block) > 0 and len(block[0]) > 0 and block[0][0] != " ":
            q_char = block[0][0]
            if all([l.startswith(q_char) for l in block]):
                # all lines start with the same character, so skip that character
                block = [l[1:] for l in block]

        # remove empty lines at beginning/end of block
        if len(block) and len(block[0]) == 0:
            block = block[1:]
        if len(block) and len(block[-1]) == 0:
            block = block[:-1]

        # prettify
        if len(block):
            # Clean up Synopsis
            if ":synopsis:" in block[0]:
                block[0] = re.sub(
                    r"\s+:synopsis:\s+(?P<syn>[\w|\s]*)",
                    r"\g<syn>",
                    block[0],
                )
        # add clickable hyperlinks to CPython docpages
        for i in range(0, len(block)):
            # hyperlink to Cpython doc pages
            # https://regex101.com/r/5RN8rj/1
            # Optionally link to python 3.4 / 3.5 documentation
            block[i] = re.sub(
                r"(\s*\|see_cpython_module\|\s+:mod:`python:(?P<mod>[\w|\s]*)`)[.]?",
                r"\g<1> https://docs.python.org/3/library/\g<mod>.html .",
                block[i],
            )
            # RST hyperlink format is not clickable in v
            # https://regex101.com/r/5RN8rj/1
            block[i] = re.sub(
                r"(.*)(?P<url><https://docs\.python\.org/.*>)(`_)",
                r"\g<1>`\g<url>",
                block[i],
            )

        #
        return block

    def fix_parameters(self, params: str):
        "change documentation parameter notation to a supported format that works for linting"
        params = params.strip()
        if not params.endswith(")"):
            # remove all after the closing bracket
            params = params[0 : params.rfind(")") + 1]

        ## Deal with SQUARE brackets first ( Documentation meaning := [optional])

        # multiple optionals
        # # .. method:: Servo.angle([angle, time=0])
        if "[angle, time=0]" in params:
            params = params.replace("[angle, time=0]", "[angle], time=0")
        # .. method:: Servo.speed([speed, time=0])
        elif "[speed, time=0]" in params:
            params = params.replace("[speed, time=0]", "[speed], time=0")

        # change [x] --> x:Optional[Any]
        params = params.replace("[", "")
        params = params.replace("]]", "")  # Q&D Hack-complex nesting
        params = params.replace("]", ": Optional[Any]")

        # deal with overloads for Flash and Partition .readblock/writeblocks
        params = params.replace("block_num, buf, offset", "block_num, buf, offset: Optional[int]")

        # Remove modulename. and Classname. from class constant
        params = self.strip_prefixes(params, strip_mod=True, strip_class=True)

        for fix in PARAM_FIXES:
            if fix[0] in params:
                params = params.replace(fix[0], fix[1])

        # formatting
        # fixme: ... not allowed in .py
        if self.target == ".py":
            params = params.replace("*, ...", "*args")
            params = params.replace("...", "*args")

        return params

    def create_update_class(self, name: str, params: str, docstr: List[str]):
        # a bit of a hack: assume no classes in classes  or functions in function
        self.leave_class()
        # TODO: Add / update information to existing class definition
        full_name = self.output_dict.find(f"class {name}")
        if full_name:
            print(_red(f"TODO: UPDATE EXISTING CLASS : {name}"))
            class_def = self.output_dict[full_name]
        else:
            # TODO: add the parent class(es) to the formal documentation
            parent = ""
            if name in CHILD_PARENT_CLASS.keys():
                parent = CHILD_PARENT_CLASS[name]

            class_def = ClassSourceDict(
                f"class {name}({parent}):",
                docstr=docstr,
            )
        if len(params) > 0:
            method = FunctionSourceDict(
                name="__init__",
                indent=class_def._indent + 4,
                definition=[f"def __init__(self, {params} -> None:"],
                docstr=[],  # todo: check if twice is needed
            )
            class_def += method
        # Append class to output
        self.output_dict += class_def
        self.current_class = name

    def parse_toc(self):
        "process table of content with additional rst files, and add / include them in the current module"
        self.log(f"# {self.line.rstrip()}")
        self.line_no += 1  # skip one line
        toctree = self.parse_docstring()
        # cleanup toctree
        toctree = [x.strip() for x in toctree if f"{self.current_module}." in x]
        # Now parse all files mentioned in the toc
        for file in toctree:
            self.read_file(Path("micropython/docs/library") / file.strip())
            self.parse()
        # reset this file to done
        self.rst_text = []
        self.line_no = 1

    def parse_module(self):
        "parse a module tag and set the module's docstring"
        self.log(f"# {self.line.rstrip()}")
        module_name = self.line.split(SEPERATOR)[-1].strip()

        self.current_module = module_name
        self.current_function = self.current_class = ""
        # get module docstring
        docstr = self.parse_docstring()

        if len(docstr) > 0:
            # Add link to online documentation
            # https://docs.micropython.org/en/v1.17/library/array.html
            if "nightly" in self.source_tag:
                version = "latest"
            else:
                version = self.source_tag.replace("_", ".")
            docstr[0] = docstr[0] + f". See: https://docs.micropython.org/en/{version}/library/{module_name}.html"

        self.output_dict.name = module_name
        self.output_dict.add_comment(f"# source version: {self.source_tag}")
        self.output_dict.add_comment(f"# origin module:: {self.filename}")
        self.output_dict.add_docstr(docstr)
        # Add additional imports to allow one module te refer to another
        if module_name in MODULE_GLUE.keys():
            self.output_dict.add_import(MODULE_GLUE[module_name])

    def parse_current_module(self):
        self.log(f"# {self.line.rstrip()}")
        module_name = self.line.split(SEPERATOR)[-1].strip()
        mod_comment = f"# + module: {self.current_module}.rst"
        self.current_module = module_name
        self.current_function = self.current_class = ""
        self.log(mod_comment)
        if NEW_OUTPUT:  # new output
            self.output_dict.name = module_name
            self.output_dict.add_comment(mod_comment)

        self.line_no += 1  # advance as we did not read any docstring
        # todo: read first block and do something with it ( for a submodule)

    def parse_function(self):
        self.log(f"# {self.line.rstrip()}")
        # this_function = self.line.split(SEPERATOR)[-1].strip()
        # name = this_function

        # Get one or more names
        function_names = self.parse_names(oneliner=False)
        docstr = self.parse_docstring()

        for this_function in function_names:
            # Parse return type from docstring
            ret_type = return_type_from_context(docstring=docstr, signature=this_function, module=self.current_module)

            ...
            # defaults
            name = params = ""
            try:
                name, params = this_function.split("(", maxsplit=1)
            except ValueError:
                print(_red(this_function))
            self.current_function = name
            if name in ("classmethod", "staticmethod"):
                # skip the classmethod and static method functions
                # no use to create stubs for these
                return

            # ussl documentation uses a ssl.foobar prefix
            for mod in self.module_names:
                if name.startswith(f"{mod}."):
                    # remove module name from the start of the function name
                    name = name[len(f"{mod}.") :]
            # fixup parameters
            params = self.fix_parameters(params)
            # assume no functions in classes
            self.leave_class()
            # if function name is the same as the module
            # then this is probably documenting a class ()

            # if the function name matches the module name then threat this as a class.
            if name in self.module_names:
                # 'Promote' function to class
                self.create_update_class(name, params, docstr)
            else:
                fn_def = FunctionSourceDict(
                    name=f"def {name}",
                    definition=[f"def {name}({params} -> {ret_type}:"],
                    docstr=docstr,
                )
                self.output_dict += fn_def

    def parse_class(self):
        self.log(f"# {self.line.rstrip()}")
        this_class = self.line.split(SEPERATOR)[-1].strip()  # raw
        if "(" in this_class:
            name, params = this_class.split("(", 2)
        else:
            name = this_class
            params = ""
        name = self.strip_prefixes(name)
        self.current_class = name
        self.current_function = ""

        self.log(f"# class:: {name} - {this_class}")
        # fixup parameters
        params = self.fix_parameters(params)
        docstr = self.parse_docstring()

        if any(":noindex:" in line for line in docstr):
            # if the class docstring contains ':noindex:' on any line then skip
            self.log(f"# Skip :noindex: class {name}")
        else:
            # write a class header
            self.create_update_class(name, params, docstr)

    def get_rst_hint(self):
        "parse the '.. <rst hint>:: ' from the current line"
        m = re.search(r"\.\.\s?(\w+)\s?::\s?", self.line)
        if m:
            return m.group(1)
        else:
            return ""

    def parse_method(self):
        name = ""
        this_method = ""
        # params = ")"
        ## py:staticmethod  - py:classmethod - py:decorator
        # ref: https://sphinx-tutorial.readthedocs.io/cheatsheet/
        self.log(f"# {self.line.rstrip()}")

        ## rst_hint is used to access the method decorator ( method, staticmethod, staticmethod ... )
        rst_hint = self.get_rst_hint()

        method_names = self.parse_names(oneliner=False)
        # filter out overloads with 'param=value' description as these can't be output (currently)
        method_names = [m for m in method_names if not "param=value" in m]

        docstr = self.parse_docstring()
        for this_method in method_names:
            try:
                name, params = this_method.split("(", 1)  # split methodname from params
            except ValueError:
                name = this_method
                params = ")"
            self.current_function = name
            # self.writeln(f"# method:: {name}")
            if "." in name:
                # todo deal with longer / deeper classes
                class_name = name.split(".")[0]
                # update current for out-of sequence method processing
                self.current_class = class_name
            else:
                # if nothing specified lets assume part of current class
                class_name = self.current_class
            name = name.split(".")[-1]  # Take only the last part from Pin.toggle

            # fixup optional [] parameters and other notations
            params = self.fix_parameters(params)

            # get or create the parent class
            full_name = self.output_dict.find(f"class {class_name}")
            if full_name:
                parent_class = self.output_dict[full_name]
            else:
                # not found, create and add new class to the output dict
                parent_class = ClassSourceDict(f"class {class_name}():")
                self.output_dict += parent_class

            # parse return type from docstring
            ret_type = return_type_from_context(docstring=docstr, signature=f"{class_name}.{name}", module=self.current_module)
            # methods have 4 flavours
            #   - __init__              (self,  <params>) -> None:
            #   - classmethod           (cls,   <params>) -> <ret_type>:
            #   - staticmethod          (       <params>) -> <ret_type>:
            #   - all other methods     (self,  <params>) -> <ret_type>:
            if name == "__init__":
                method = FunctionSourceDict(
                    name=f"def {name}",
                    indent=parent_class._indent + 4,
                    definition=[f"def __init__(self, {params} -> None:"],
                    docstr=docstr,
                )
                parent_class += method
            elif rst_hint == "classmethod":
                method = FunctionSourceDict(
                    decorators=["@classmethod"],
                    name=f"def {name}",
                    indent=parent_class._indent + 4,
                    definition=[f"def {name}(cls, {params} -> {ret_type}:"],
                    docstr=docstr,
                )
                parent_class += method

            elif rst_hint == "staticmethod":
                method = FunctionSourceDict(
                    decorators=["@staticmethod"],
                    name=f"def {name}",
                    indent=parent_class._indent + 4,
                    definition=[f"def {name}({params} -> {ret_type}:"],
                    docstr=docstr,
                )
                parent_class += method
            else:  # just plain method
                method = FunctionSourceDict(
                    name=f"def {name}",
                    indent=parent_class._indent + 4,
                    definition=[f"def {name}(self, {params} -> {ret_type}:"],
                    docstr=docstr,
                )
                parent_class += method

    def parse_exception(self):
        self.log(f"# {self.line.rstrip()}")
        name = self.line.split(SEPERATOR)[1].strip()
        # TODO : check name scope : Module.class.<name>
        if "." in name:
            name = name.split(".")[-1]  # Take only the last part from Pin.toggle
        except_1 = ClassSourceDict(name=f"class {name}(BaseException) : ...", docstr=[], init="")
        self.output_dict += except_1
        # no docstream read (yet) , so need to advance to next line
        self.line_no += 1
        # class Exception(BaseException): ...

    def parse_name(self, line: str = None):
        "get the constant/function/class name from a line with an identifier"
        # this_const = self.line.split(SEPERATOR)[-1].strip()
        # name = this_const
        # name = this_const.split(".")[1]  # Take only the last part from Pin.toggle

        if line:
            return line.split(SEPERATOR)[-1].strip()
        else:
            return self.line.split(SEPERATOR)[-1].strip()

    def parse_names(self, oneliner: bool = True):
        """get a list of constant/function/class names from and following a line with an identifier
        advances the linecounter

        oneliner :  treat a line with commas as multiple names (used for constants)
        """
        names: List[str] = []
        if oneliner:
            names += self.parse_name().split(",")
        else:
            names += [self.parse_name()]

        m = re.search(r"..\s?\w+\s?::\s?", self.line)
        if m:
            col = m.end()
        else:
            raise KeyError
        counter = 1
        while (
            self.line_no + counter <= self.max_line
            and self.rst_text[self.line_no + counter].startswith(" " * col)
            and not self.rst_text[self.line_no + counter][col + 1].isspace()
        ):
            if self.verbose:
                print(_green("Sequence detected"))
            names.append(self.parse_name(self.rst_text[self.line_no + counter]))
            counter += 1
        # now advance the linecounter
        self.line_no += counter - 1
        # clean up before returning
        return [n.strip() for n in names if n.strip() != "etc."]

    def parse_data(self):
        # todo: find a way to reliably add Constants at the correct level
        # Note : makestubs has no issue with this
        self.log(f"# {self.line.rstrip()}")
        # Get one or more names
        names = self.parse_names()

        # get module docstring
        docstr = self.parse_docstring()

        # deal with documentation wildcards
        for name in names:

            type = return_type_from_context(docstring=docstr, signature=name, module=self.current_module, literal=True)
            if type in ["None"]:  # None does not make sense
                type = "Any"  # perhaps default to Int ?
            name = self.strip_prefixes(name)
            self.output_dict.add_constant_smart(name=name, type=type, docstr=docstr)

    def parse(self):
        self.line_no = 0
        while self.line_no < len(self.rst_text):
            line = self.line
            rst_hint = self.get_rst_hint()
            #    self.writeln(">"+line)
            if rst_hint == "module":
                self.parse_module()
            elif rst_hint == "currentmodule":
                self.parse_current_module()
            elif rst_hint == "function":
                self.parse_function()

            elif rst_hint == "class":
                self.parse_class()
            elif rst_hint == "method" or rst_hint == "staticmethod" or rst_hint == "classmethod":
                self.parse_method()
            elif rst_hint == "exception":
                self.parse_exception()
            elif rst_hint == "data":
                self.parse_data()

            elif rst_hint == "toctree":
                self.parse_toc()
                # not this will be the end of this file processing.

            elif len(rst_hint) > 0:
                # something new / not yet parsed
                self.log(f"# {line.rstrip()}")
                if self.verbose:
                    print(_red(line.rstrip()))
                self.line_no += 1
            else:
                # NOTHING TO SEE HERE , MOVE ON
                self.line_no += 1
            #  TODO: rebuild this into the NEW_OUTPUT way of working
            #     if self.gather_docs and len(docstr) > 0:
            #         self.return_info.append(
            #             (
            #                 self.current_module,
            #                 self.current_class,
            #                 self.current_function,
            #                 self.last_line,
            #                 docstr,
            #             )
            #         )

        # now clean up
        self.prepare_output()


def generate_from_rst(rst_folder: Path, dst_folder: Path, v_tag: str, black=True, pattern: str = "*.rst") -> int:
    if not dst_folder.exists():
        dst_folder.mkdir(parents=True)
    # no index, and module.xxx.rst is included in module.py
    files = [f for f in rst_folder.glob(pattern) if f.stem != "index" and "." not in f.stem]
    for file in files:
        reader = RSTReader(v_tag)
        reader.read_file(file)
        reader.parse()
        reader.write_file((dst_folder / file.name).with_suffix(".py"))
        del reader

    if black:
        try:

            cmd = ["black", str(dst_folder)]
            if sys.version_info.major == 3 and sys.version_info.minor == 7:
                # black on python 3.7 does not like some function defs
                # def sizeof(struct, layout_type=NATIVE, /) -> int:
                cmd += ["--fast"]
            result = subprocess.run(cmd, capture_output=False, check=True, shell=True)
            if result.returncode != 0:
                raise Exception(result.stderr.decode("utf-8"))
        except subprocess.SubprocessError:
            print(_red("some of the files are not in a proper format"))

    return len(files)


if __name__ == "__main__":
    base_path = Path("micropython")
    # base_path = Path("../pycopy")
    v_tag = git.get_tag(base_path.as_posix())
    if not v_tag:
        # if we can't find a tag , bail
        raise ValueError

    rst_folder = base_path / "docs" / "library"
    dst_folder = Path("all-stubs") / base_path.stem / (flat_version(v_tag, keep_v=True) + "-docs")

    generate_from_rst(rst_folder, dst_folder, v_tag)
    # generate_from_rst(rst_folder, dst_folder, v_tag, pattern="binascii.rst")  # debug
