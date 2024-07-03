""" 
Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking 
using a custom-built parser to read and process the micropython RST files
- generates:
    - modules 
        - docstrings
    - function definitions 
        - function parameters based on documentation
        - docstrings
    - classes
        - docstrings
        - __init__ method
        - parameters based on documentation for class 
        - methods
            - parameters based on documentation for the method
            - docstrings

    - exceptions

- Tries to determine the return type by parsing the docstring.
    - Imperative verbs used in docstrings have a strong correlation to return -> None
    - recognizes documented Generators, Iterators, Callable
    - Coroutines are identified based tag "This is a Coroutine". Then if the return type was Foo, it will be transformed to : Coroutine[Foo]
    - a static Lookup list is used for a few methods/functions for which the return type cannot be determined from the docstring. 
    - add NoReturn to a few functions that never return ( stop / deepsleep / reset )
    - if no type can be detected the type `Any` or `Incomplete` is used

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

- Add GLUE imports to allow specific modules to import specific others. 

- Repeats of definitions in the rst file for similar functions or literals
    - CONSTANTS ( module and Class level )
    - functions
    - methods

- Child/ Parent classes
    are added based on a (manual) lookup table CHILD_PARENT_CLASS

"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from mpflash.logger import log
from mpflash.versions import V_PREVIEW
from stubber.rst import (
    CHILD_PARENT_CLASS,
    MODULE_GLUE,
    PARAM_FIXES,
    RST_DOC_FIXES,
    TYPING_IMPORT,
    ClassSourceDict,
    FunctionSourceDict,
    ModuleSourceDict,
    return_type_from_context,
)
from stubber.rst.lookup import Fix
from stubber.utils.config import CONFIG

SEPERATOR = "::"


class FileReadWriter:
    """base class for reading rst files"""

    def __init__(self):
        self.filename = ""
        # input buffer
        self.rst_text: List[str] = []
        self.max_line = 0
        self.line_no: int = 0  # current Linenumber used during parsing.
        self.last_line = ""

        # Output buffer
        self.output: List[str] = []

    def read_file(self, filename: Path):
        log.trace(f"Reading : {filename}")
        # ignore Unicode decoding issues
        with open(filename, errors="ignore", encoding="utf8") as file:
            self.rst_text = file.readlines()
        # Replace incorrect definitions in .rst files with better ones
        for FIX in RST_DOC_FIXES:
            self.rst_text = [line.replace(FIX[0], FIX[1]) for line in self.rst_text]
        # some lines now may have \n sin them , so re-join and re-split the lines
        self.rst_text = "".join(self.rst_text).splitlines(keepends=True)

        self.filename = filename.as_posix()  # use fwd slashes in origin
        self.max_line = len(self.rst_text) - 1

    def write_file(self, filename: Path) -> bool:
        try:
            log.info(f" - Writing to: {filename}")
            with open(filename, mode="w", encoding="utf8") as file:
                file.writelines(self.output)
        except OSError as e:
            log.error(e)
            return False
        return True

    @property
    def line(self) -> str:
        "get the current line from input, also stores this as last_line to allow for inspection and dumping the json file"
        if self.line_no >= 0 and self.line_no <= self.max_line:
            self.last_line = self.rst_text[self.line_no]
        else:
            self.last_line = ""
        return self.last_line

    @staticmethod
    def is_balanced(s: str) -> bool:
        """
        Check if a string has balanced parentheses
        """
        return False if s.count("(") != s.count(")") else s.count("{") == s.count("}")

    def extend_and_balance_line(self) -> str:
        """
        Append the current line + next line in order to try to balance the parentheses
        in order to do this the rst_test array is changed by the function
        and max_line is adjusted
        """
        append = 0
        newline = self.rst_text[self.line_no]
        while not self.is_balanced(newline) and self.line_no >= 0 and (self.line_no + append + 1) <= self.max_line:
            append += 1
            # concat the lines
            newline += self.rst_text[self.line_no + append]
        # only update line if things balanced out correctly
        if self.is_balanced(newline):
            self.rst_text[self.line_no] = newline
            for _ in range(append):
                self.rst_text.pop(self.line_no + 1)
                self.max_line -= 1
        # reprocess line
        return self.line


class RSTReader(FileReadWriter):
    docstring_anchors = [
        ".. note::",
        ".. data:: Arguments:",
        ".. data:: Options:",
        ".. data:: Returns:",
        ".. data:: Raises:",
        ".. admonition::",
    ]
    # considered part of the docstrings

    def __init__(self):
        self.current_module = ""
        self.current_class = ""
        self.current_function = ""  # function & method
        super().__init__()

    def read_file(self, filename: Path):
        super().read_file(filename)
        self.current_module = filename.stem  # just to be sure

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

    @property
    def at_anchor(self) -> bool:
        "Stop at anchor '..something' ( however .. note: and ..data:: should be added)"
        line = self.rst_text[self.line_no].lstrip()
        # anchors that are considered part of the docstring
        # Check if the line starts with '..' but not any of the docstring_anchors.
        if line.startswith(".."):
            return not any(line.startswith(anchor) for anchor in self.docstring_anchors)
        return False

        # return _l.startswith("..") and not any(_l.startswith(a) for a in self.docstring_anchors)

    # @property
    def at_heading(self, large=False) -> bool:
        "stop at heading"
        u_line = self.rst_text[min(self.line_no + 1, self.max_line - 1)].rstrip()
        # Heading  ---, ==, ~~~
        underlined = u_line.startswith("---") or u_line.startswith("===") or u_line.startswith("~~~")
        if underlined and self.line_no > 0:
            # check if previous line is a heading
            line = self.rst_text[self.line_no].strip()
            if line:
                # module docstrings can be a bit larger than normal
                if not large and len(line) == len(u_line):
                    # heading is same length as underlined
                    # for most docstrings that is a sensible boundary
                    return True
                line = line.split()[0]
                # stopwords in headings
                return line.lower() in [
                    "classes",
                    "functions",
                    "methods",
                    "constants",
                    "exceptions",
                    "constructors",
                    "class",
                    "common",
                    "general",
                    # below are tuning based on module level docstrings
                    "time",
                    "pio",
                    "memory",
                ]
        return False

    def read_docstring(self, large: bool = False) -> List[str]:
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
                and not self.at_anchor  # stop at next anchor ( however .. note: and a few other anchors should be added)
                and not self.at_heading(large)  # stop at next heading
            ):
                line = self.rst_text[self.line_no]
                block.append(line.rstrip())
                self.line_no += 1  # advance line
        except IndexError:
            pass

        # remove empty lines at beginning/end of block
        block = self.clean_docstr(block)
        # add clickable hyperlinks to CPython docpages
        block = self.add_link_to_docsstr(block)
        # make sure the first char of the first line is a capital
        if len(block) > 0 and len(block[0]) > 0:
            block[0] = block[0][0].upper() + block[0][1:]
        return block

    @staticmethod
    def clean_docstr(block: List[str]):
        """Clean up a docstring"""
        # if a Quoted Literal Block , then remove the first character of each line
        # https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#quoted-literal-blocks
        if block and len(block[0]) > 0 and block[0][0] != " ":
            q_char = block[0][0]
            if all(l.startswith(q_char) for l in block):
                # all lines start with the same character, so skip that character
                block = [l[1:] for l in block]
        # rstrip all lines
        block = [l.rstrip() for l in block]
        # remove empty lines at beginning/end of block
        while len(block) and len(block[0]) == 0:
            block = block[1:]
        while len(block) and len(block[-1]) == 0:
            block = block[:-1]

        # Clean up Synopsis
        if len(block) and ":synopsis:" in block[0]:
            block[0] = re.sub(
                r"\s+:synopsis:\s+(?P<syn>[\w|\s]*)",
                r"\g<syn>",
                block[0],
            )
        return block

    @staticmethod
    def add_link_to_docsstr(block: List[str]):
        """Add clickable hyperlinks to CPython docpages"""
        for i in range(len(block)):
            # hyperlink to Cpython doc pages
            # https://regex101.com/r/5RN8rj/1
            # Link to python 3 documentation
            _l = re.sub(
                r"(\s*\|see_cpython_module\|\s+:mod:`python:(?P<mod>[\w|\s]*)`)[.]?",
                r"\g<1> https://docs.python.org/3/library/\g<mod>.html .",
                block[i],
            )
            # RST hyperlink format is not clickable in VSCode so convert to markdown format
            # https://regex101.com/r/5RN8rj/1
            _l = re.sub(
                r"(.*)(?P<url><https://docs\.python\.org/.*>)(`_)",
                r"\g<1>`\g<url>",
                _l,
            )
            # Clean up note and other docstring anchors
            _l = _l.replace(".. note:: ", "``Note:`` ")
            _l = _l.replace(".. data:: ", "")
            _l = _l.replace(".. admonition:: ", "")
            _l = _l.replace("|see_cpython_module|", "CPython module:")
            # clean up unsupported escape sequences in rst
            _l = _l.replace(r"\ ", " ")
            _l = _l.replace(r"\*", "*")
            block[i] = _l
        return block

    def get_rst_hint(self):
        "parse the '.. <rst hint>:: ' from the current line"
        m = re.search(r"\.\.\s?(\w+)\s?::\s?", self.line)
        return m[1] if m else ""

    def strip_prefixes(self, name: str, strip_mod: bool = True, strip_class: bool = False):
        "Remove the modulename. and or the classname. from the begining of a name"
        prefixes = self.module_names if strip_mod else []
        if strip_class and self.current_class != "":
            prefixes += [self.current_class]
        for prefix in prefixes:
            if len(prefix) > 1 and prefix + "." in name:
                name = name.replace(prefix + ".", "")
        return name


class RSTParser(RSTReader):
    """
    Parse the RST file and create a ModuleSourceDict
    most methods have side effects
    """

    target = ".py"  # py/pyi
    # TODO: Move to lookup.py
    PARAM_RE_FIXES = [
        Fix(r"\[angle, time=0\]", "[angle], time=0", is_re=True),  # fix: method:: Servo.angle([angle, time=0])
        Fix(r"\[speed, time=0\]", "[speed], time=0", is_re=True),  # fix: .. method:: Servo.speed([speed, time=0])
        Fix(r"\[service_id, key=None, \*, \.\.\.\]", "[service_id], [key], *, ...", is_re=True),  # fix: network - AbstractNIC.connect
    ]

    def __init__(self, v_tag: str) -> None:
        super().__init__()
        self.output_dict: ModuleSourceDict = ModuleSourceDict("")
        self.output_dict.add_import(TYPING_IMPORT)
        self.return_info: List[Tuple] = []  # development aid only
        self.source_tag = v_tag
        self.source_release = v_tag

    def leave_class(self):
        if self.current_class != "":
            self.current_class = ""

    def fix_parameters(self, params: str, name: str = "") -> str:
        """Patch / correct the documentation parameter notation to a supported format that works for linting.
        - params is the string containing the parameters as documented in the rst file
        - name is the name of the function or method or Class
        """
        params = params.strip()
        if not params.endswith(")"):
            # remove all after the closing bracket
            params = params[: params.rfind(")") + 1]

        # Remove modulename. and Classname. from class constant
        params = self.strip_prefixes(params, strip_mod=True, strip_class=True)

        ## Deal with SQUARE brackets first ( Documentation meaning := [optional])

        for fix in self.PARAM_RE_FIXES:
            params = self.apply_fix(fix, params, name)

        # ###########################################################################################################
        # does not look cool, but works really well
        # change [x] --> x:Optional[Any]
        params = params.replace("[", "")
        params = params.replace("]]", "")  # Q&D Hack-complex nesting

        # Handle Optional arguments
        # Optional step 1: [x] --> x: Optional[Any]=None
        params = params.replace("]", ": Optional[Any]=None")
        # Optional step 2: x: Optional[Any]=None='abc' --> x: Optional[Any]='abc'
        params = re.sub(r": Optional\[Any\]=None\s*=", r": Optional[Any]=", params)
        # Optional step 3: fix ...
        params = re.sub(r"\.\.\.: Optional\[Any\]=None", r"...", params)
        # ###########################################################################################################

        for fix in PARAM_FIXES:
            if fix.module == self.current_module or not fix.module:
                params = self.apply_fix(fix, params, name)

        # # formatting
        # # fixme: ... not allowed in .py
        if self.target == ".py":
            params = params.replace("*, ...", "*args, **kwargs")
            params = params.replace("...", "*args, **kwargs")

        return params.strip()

    @staticmethod
    def apply_fix(fix: Fix, params: str, name: str = ""):
        if fix.name and fix.name != name:
            return params
        return re.sub(fix.from_, fix.to, params) if fix.is_re else params.replace(fix.from_, fix.to)

    def create_update_class(self, name: str, params: str, docstr: List[str]):
        # a bit of a hack: assume no classes in classes  or functions in function
        self.leave_class()
        if full_name := self.output_dict.find(f"class {name}"):
            log.warning(f"TODO: UPDATE EXISTING CLASS : {name}")
            class_def = self.output_dict[full_name]
        else:
            parent = CHILD_PARENT_CLASS[name] if name in CHILD_PARENT_CLASS.keys() else ""
            if parent == "" and (name.endswith("Error") or name.endswith("Exception")):
                parent = "Exception"
            class_def = ClassSourceDict(
                f"class {name}({parent}):",
                docstr=docstr,
            )
        if params != "":
            method = FunctionSourceDict(
                name="__init__",
                indent=class_def.indent + 4,
                definition=[f"def __init__(self, {params} -> None:"],
                docstr=[],  # todo: check if twice is needed
            )
            class_def += method
        # Append class to output
        self.output_dict += class_def
        self.current_class = name

    def parse_toc(self):
        "process table of content with additional rst files, and add / include them in the current module"
        log.trace(f"# {self.line.rstrip()}")
        self.line_no += 1  # skip one line
        toctree = self.read_docstring()
        # cleanup toctree
        toctree = [x.strip() for x in toctree if f"{self.current_module}." in x]
        # Now parse all files mentioned in the toc
        for file in toctree:
            #
            file_path = CONFIG.mpy_path / "docs" / "library" / file.strip()
            self.read_file(file_path)
            self.parse()
        # reset this file to done
        self.rst_text = []
        self.line_no = 1

    def parse_module(self):
        "parse a module tag and set the module's docstring"
        log.trace(f"# {self.line.rstrip()}")
        module_name = self.line.split(SEPERATOR)[-1].strip()

        self.current_module = module_name
        self.current_function = self.current_class = ""
        # get module docstring
        docstr = self.read_docstring(large=True)

        if len(docstr) > 0:
            # Add link to online documentation
            # https://docs.micropython.org/en/v1.17/library/array.html
            if "nightly" in self.source_tag:
                version = V_PREVIEW
            else:
                version = self.source_tag.replace("_", ".")  # TODO Use clean_version(self.source_tag)
            docstr[0] = f"{docstr[0]}.\n\nMicroPython module: https://docs.micropython.org/en/{version}/library/{module_name}.html"

        self.output_dict.name = module_name
        self.output_dict.add_comment(f"# source version: {self.source_tag}")
        self.output_dict.add_comment(f"# origin module:: {self.filename}")
        self.output_dict.add_docstr(docstr)
        # Add additional imports to allow one module te refer to another
        if module_name in MODULE_GLUE.keys():
            self.output_dict.add_import(MODULE_GLUE[module_name])

    def parse_current_module(self):
        log.trace(f"# {self.line.rstrip()}")
        module_name = self.line.split(SEPERATOR)[-1].strip()
        mod_comment = f"# + module: {self.current_module}.rst"
        self.current_module = module_name
        self.current_function = self.current_class = ""
        log.debug(mod_comment)
        self.output_dict.name = module_name
        self.output_dict.add_comment(mod_comment)
        self.line_no += 1  # advance as we did not read any docstring

    def parse_function(self):
        log.trace(f"# {self.line.rstrip()}")
        # this_function = self.line.split(SEPERATOR)[-1].strip()
        # name = this_function

        # Get one or more names
        function_names = self.parse_names(oneliner=False)
        docstr = self.read_docstring()

        for this_function in function_names:
            # Parse return type from docstring
            ret_type = return_type_from_context(docstring=docstr, signature=this_function, module=self.current_module)

            # defaults
            name = params = ""
            try:
                name, params = this_function.split("(", maxsplit=1)
            except ValueError:
                log.error(this_function)
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
            params = self.fix_parameters(params, name)
            # ASSUME no functions in classes,
            # so with ther cursor at a function this probably means that we are no longer in a class
            self.leave_class()

            fn_def = FunctionSourceDict(
                name=f"def {name}",
                definition=[f"def {name}({params} -> {ret_type}:"],
                docstr=docstr,
            )
            self.output_dict += fn_def

    def parse_class(self):
        log.trace(f"# {self.line.rstrip()}")
        this_class = self.line.split(SEPERATOR)[-1].strip()  # raw
        if "(" in this_class:
            name, params = this_class.split("(", 2)
        else:
            name = this_class
            params = ""
        name = self.strip_prefixes(name)
        self.current_class = name
        self.current_function = ""

        log.trace(f"# class:: {name} - {this_class}")
        # fixup parameters
        params = self.fix_parameters(params, f"{name}.__init__")
        docstr = self.read_docstring()

        if any(":noindex:" in line for line in docstr):
            # if the class docstring contains ':noindex:' on any line then skip
            log.trace(f"# Skip :noindex: class {name}")
        else:
            # write a class header
            self.create_update_class(name, params, docstr)

    def parse_method(self):
        name = ""
        this_method = ""
        ## py:staticmethod  - py:classmethod - py:decorator
        # ref: https://sphinx-tutorial.readthedocs.io/cheatsheet/
        log.trace(f"# {self.line.rstrip()}")
        if not self.is_balanced(self.line):
            self.extend_and_balance_line()

        ## rst_hint is used to access the method decorator ( method, staticmethod, staticmethod ... )
        rst_hint = self.get_rst_hint()

        method_names = self.parse_names(oneliner=False)
        # filter out overloads with 'param=value' description as these can't be output (currently)
        method_names = [m for m in method_names if "param=value" not in m]

        docstr = self.read_docstring()
        for this_method in method_names:
            try:
                name, params = this_method.split("(", 1)  # split methodname from params
            except ValueError:
                name = this_method
                params = ")"
            is_async = "async" in name
            self.current_function = name
            # self.writeln(f"# method:: {name}")
            if "." in name:
                # todo deal with longer / deeper classes
                class_name = name.split(".")[0]
                # ESPnow.rst has a few methods that are written as `async AIOESPNow.__anext__()`
                if is_async:
                    class_name = class_name.replace("async ", "").strip()
                # update current for out-of sequence method processing
                self.current_class = class_name
            else:
                # if nothing specified lets assume part of current class
                class_name = self.current_class
            name = name.split(".")[-1]  # Take only the last part from Pin.toggle

            if full_name := self.output_dict.find(f"class {class_name}"):
                parent_class = self.output_dict[full_name]
            else:
                # not found, create and add new class to the output dict
                parent_class = ClassSourceDict(f"class {class_name}():")
                self.output_dict += parent_class

            # fixup optional [] parameters and other notations
            params = self.fix_parameters(params, f"{class_name}.{name}")

            # parse return type from docstring
            ret_type = return_type_from_context(docstring=docstr, signature=f"{class_name}.{name}", module=self.current_module)
            # methods have 4 flavours
            #   - __init__              (self,  <params>) -> None:
            #   - classmethod           (cls,   <params>) -> <ret_type>:
            #   - staticmethod          (       <params>) -> <ret_type>:
            #   - all other methods     (self,  <params>) -> <ret_type>:
            if name == "__init__":
                # avoid params starting with `self ,`
                params = self.lstrip_self(params)
                method = FunctionSourceDict(
                    name=f"def {name}",
                    indent=parent_class.indent + 4,
                    definition=[f"def __init__(self, {params} -> None:"],
                    docstr=docstr,
                )
            elif rst_hint == "classmethod":
                method = FunctionSourceDict(
                    decorators=["@classmethod"],
                    name=f"def {name}",
                    indent=parent_class.indent + 4,
                    definition=[f"def {name}(cls, {params} -> {ret_type}:"],
                    docstr=docstr,
                    is_async=is_async,
                )
            elif rst_hint == "staticmethod":
                method = FunctionSourceDict(
                    decorators=["@staticmethod"],
                    name=f"def {name}",
                    indent=parent_class.indent + 4,
                    definition=[f"def {name}({params} -> {ret_type}:"],
                    docstr=docstr,
                    is_async=is_async,
                )
            else:  # just plain method
                # avoid params starting with `self ,`
                params = self.lstrip_self(params)
                method = FunctionSourceDict(
                    name=f"def {name}",
                    indent=parent_class.indent + 4,
                    definition=[f"def {name}(self, {params} -> {ret_type}:"],
                    docstr=docstr,
                    is_async=is_async,
                )

            parent_class += method

    def lstrip_self(self, params: str):
        """
        To avoid duplicate selfs,
        Remove `self,` from the start of the parameters
        """
        params = params.lstrip()

        for start in ["self,", "self ,", "self ", "self"]:
            if params.startswith(start):
                params = params[len(start) :]
        return params

    def parse_exception(self):
        log.trace(f"# {self.line.rstrip()}")
        name = self.line.split(SEPERATOR)[1].strip()
        if name == "Exception":
            # no need to redefine Exception
            self.line_no += 1
            return
        # Take only the last part from module.ExceptionX
        if "." in name:
            name = name.split(".")[-1]
        except_1 = ClassSourceDict(name=f"class {name}(Exception) : ...", docstr=[], init="")
        self.output_dict += except_1
        # no docstream read (yet) , so need to advance to next line
        self.line_no += 1

    def parse_name(self, line: Optional[str] = None):
        "get the constant/function/class name from a line with an identifier"
        # '.. data:: espnow.MAX_DATA_LEN(=250)\n'
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
        names += self.parse_name().split(",") if oneliner else [self.parse_name()]
        m = re.search(r"..\s?\w+\s?::\s?", self.line)
        if not m:  # pragma: no cover
            raise KeyError
        col = m.end()
        counter = 1
        while (
            self.line_no + counter <= self.max_line
            and self.rst_text[self.line_no + counter].startswith(" " * col)
            and not self.rst_text[self.line_no + counter][col + 1].isspace()
        ):
            log.trace("Sequence detected")
            names.append(self.parse_name(self.rst_text[self.line_no + counter]))
            counter += 1
        # now advance the linecounter
        self.line_no += counter - 1
        # clean up before returning
        names = [n.strip() for n in names if n.strip() != "etc."]  # remove etc.
        return names

    def parse_data(self):
        """process ..data:: lines ( one or more)
        Note: some data islands are included in the docstring of the module/class/function as the ESPNow documentation started to use this pattern.
        """
        log.trace(f"# {self.line.rstrip()}")
        # Get one or more names
        names = self.parse_names()

        # get module docstring
        docstr = self.read_docstring()

        # deal with documentation wildcards
        for name in names:
            r_type = return_type_from_context(docstring=docstr, signature=name, module=self.current_module, literal=True)
            if r_type in ["None"]:  # None does not make sense
                r_type = "Incomplete"  # Default to Incomplete/ Unknown / int
            name = self.strip_prefixes(name)
            self.output_dict.add_constant_smart(name=name, type=r_type, docstr=docstr)

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
            elif rst_hint in ["method", "staticmethod", "classmethod"]:
                self.parse_method()
            elif rst_hint == "exception":
                self.parse_exception()
            elif rst_hint == "data":
                self.parse_data()
            elif rst_hint == "toctree":
                self.parse_toc()
                # Note: this will end the processing of this file.
            elif len(rst_hint) > 0:
                # something new / not yet parsed/understood
                self.line_no += 1
                log.trace(f"# {line.rstrip()}")
            else:
                # NOTHING TO SEE HERE , MOVE ON
                self.line_no += 1


#################################################################################################################
class RSTWriter(RSTParser):
    """
    Reads, parses and writes
    """

    def __init__(self, v_tag="v1.xx"):
        super().__init__(v_tag=v_tag)

    def write_file(self, filename: Path) -> bool:
        self.prepare_output()
        return super().write_file(filename)

    def prepare_output(self):
        "Remove trailing spaces and commas from the output."
        lines = str(self.output_dict).splitlines(keepends=True)
        self.output = lines
        for i in range(len(self.output)):
            for name in ("self", "cls"):
                if f"({name}, ) ->" in self.output[i]:
                    self.output[i] = self.output[i].replace(f"({name}, ) ->", f"({name}) ->")
