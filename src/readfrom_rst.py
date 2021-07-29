""" Work in Progress
    Read the Micropython library documentation files and use them to build stubs that can be used for static typechecking 

    - uses a custom build parser to read the RST files 
    - generates 
        modules 
            - docstrings
        function definitions 
            - function parameters based on documentation
            - docstrings
        classes
            - docstrings
            __init__ method
            - parameters based on documentation for class 
            methods
                - parameters based on documentation for the method
                - docstrings
        exceptions

    The generated stub files are formatted using `black` and checked for validity using `pyright`

    WIP 
    - tries to determine the return type by parsing the docstring 
    FIX Needed 
        - improve docstring extraction 
            - move report out of docstring to fix name skew 
            - add class/function signature to export 
        - End of debug Class marker is now broken , reports new class
                # .. toctree::
                # .. currentmodule:: network
                # currentmodule:: network
                # .. class:: WLAN(interface_id)
                # class:: WLAN
                # End of class: WLAN

    Not yet implemented 
    - Literals 
    - ordering of inter-dependent classes in the same module
    - add superclasses ( must be based on a external list as this is currently not documented as part of the class)
            - WLAN(AbstractNIC)
            - WLANWiPy(AbstractNIC)
            
            - Signal(Pin)
"""

import json
import re
import subprocess
from typing import Dict, List, Tuple
from pathlib import Path
import basicgit as git
from utils import flat_version


def _color(c, *args) -> str:
    s = str(*args)
    return f"\033[{c}m {s}\033[00m"


def _green(*args) -> str:
    return _color(92, *args)


def _red(*args) -> str:
    return _color(91, *args)


# Development
GATHER_DOC = True


class RSTReader:
    __debug = True  # a
    verbose = False
    no_explicit_init = False  # True to avoid overloading __init__

    def __init__(self, v_tag="v1.xx"):
        self.sep = "::"
        self.filename = ""

        self.current_module = ""
        self.current_class = ""
        self.current_function = ""  # function & method

        self.depth = 0
        self.rst_text: List[str] = []
        self.max_line = 0
        self.output: List[str] = []
        self.source_tag = v_tag
        self.target = ".py"  # py/pyi
        self.classes: List[str] = []  # is this used ?
        self.return_info: List[Tuple] = []  # development aid only

        self.writeln("from typing import Any, Optional, Union, Tuple\n")

    def log(self, *arg):
        if self.verbose or 1:
            print(*arg)
            self.writeln(*arg)

    @property
    def indent(self):
        return " " * self.depth

    def updent(self, n=4):
        self.depth += n

    def dedent(self, n=4):
        self.depth = max(0, self.depth - n)

    def leave_class(self):
        if self.current_class != "":
            if self.verbose or self.__debug:
                self.writeln(f"{self.indent}# End of class: {self.current_class}")
                self.writeln(f"{self.indent}# ..................................")
            self.dedent()
            self.current_class = ""

    def read_file(self, filename):
        print(f" - Reading from: {filename}")
        # ingore Unicode decoding issues
        with open(filename, errors="ignore", encoding="utf8") as file:
            self.rst_text = file.readlines()
        self.filename = filename
        self.max_line = len(self.rst_text) - 1

    def writeln(self, *arg):
        "store transformed output in a buffer"
        new = str(*arg)
        self.output.append(new + "\n")
        if self.verbose:
            print(new)

    def _cleanup(self):
        "clean up some trailing spaces and commas"
        for n in range(0, len(self.output)):
            if "(self, ) ->" in self.output[n]:
                self.output[n] = self.output[n].replace("(self, ) ->", "(self) ->")

    def write_file(self, filename: Path) -> bool:
        self._cleanup()
        try:
            print(f" - Writing to: {filename}")
            with open(filename, mode="w", encoding="utf8") as file:
                file.writelines(self.output)
        except OSError as e:
            print(e)
            return False
        if GATHER_DOC:
            print(f" - Writing to: {filename}")
            with open(filename.with_suffix(".json"), mode="w", encoding="utf8") as file:
                json.dump(self.return_info, file, ensure_ascii=False, indent=4)
            self.return_info = []

        return True

    def read_textblock(self, n: int) -> Tuple[int, List[str]]:
        if n >= len(self.rst_text):
            raise IndexError
        block: List[str] = []
        n += 1  # advance over current line
        try:
            while (
                n < len(self.rst_text)
                and not self.rst_text[n]
                .lstrip()
                .startswith(
                    ".."
                )  # stop at anchor ( however .. note: could be considered tp be added)
                and not self.rst_text[min(n + 1, self.max_line)].startswith("--")  # Heading --
                and not self.rst_text[min(n + 1, self.max_line)].startswith("==")  # Heading ==
                and not self.rst_text[min(n + 1, self.max_line)].startswith("~~")  # Heading ~~
            ):
                line = self.rst_text[n]
                block.append(line.rstrip())
                n += 1  # advance line
        except IndexError:
            pass
        # remove empty lines at beginning/end of block
        if len(block) and len(block[0]) == 0:
            block = block[1:]
        if len(block) and len(block[-1]) == 0:
            block = block[:-1]
        if GATHER_DOC and len(block) > 0:
            self.return_info.append(
                (self.current_module, self.current_class, self.current_function, block)
            )
        return (n, block)

    def fix_parameters(self, params: str):
        "change parameter notation issues into a supported version"
        params = params.strip()
        if not params.endswith(")"):
            # remove all after the closing bracket
            params = params[0 : params.rfind(")") + 1]
        # multiple optionals
        # # .. method:: Servo.angle([angle, time=0])
        if "[angle, time=0]" in params:
            params = params.replace("[angle, time=0]", "[angle], time=0")
        # .. method:: Servo.speed([speed, time=0])
        elif "[speed, time=0]" in params:
            params = params.replace("[speed, time=0]", "[speed], time=0")

        # sublist parameters are not supported in python 3
        elif "(adcx, adcy, ...)" in params:
            # method:: ADC.read_timed_multi((adcx, adcy, ...), (bufx, bufy, ...), timer)
            params = params.replace("(adcx, adcy, ...), (bufx, bufy, ...)", "adcs, bufs")
        elif "(ip, subnet, gateway, dns)" in params:
            # network: # .. method:: AbstractNIC.ifconfig([(ip, subnet, gateway, dns)])
            params = params.replace("(ip, subnet, gateway, dns)", "configtuple")

        # pyb  .. function:: hid((buttons, x, y, z))
        params = params.replace("(buttons, x, y, z)", "hidtuple")

        # esp v1.15.2 .. function:: getaddrinfo((hostname, port, lambda))
        params = params.replace("(hostname, port, lambda)", "tuple")

        # change [x] --> x:Optional[Any]
        params = params.replace("[", "")
        params = params.replace("]]", "")  # Q&D Hack-complex nesting
        params = params.replace("]", ": Optional[Any]")

        # # change weirdly written wildcards \* --> *
        wilds = (
            ("\\*", "*"),
            (r"\**", "*"),
            ("**", "*"),
        )
        for pair in wilds:
            if pair[0] in params:
                params = params.replace(pair[0], pair[1])
        # ... not allowed in .py
        if self.target == ".py":
            params = params.replace("*, ...", "*args")
            params = params.replace("...", "*args")
        # todo: change or remove value hints (...|....)
        # params = params.replace("pins=(SCK, MOSI, MISO)", "")  # Q&D

        # param default to module constant
        #   def foo(x =module.CONST): ...
        # param default to class constant
        #   def __init__(self, x =class.CONST): ...
        for prefix in (f"{self.current_module}.", f"{self.current_class}."):
            if len(prefix) > 1 and prefix in params:
                params = params.replace(prefix, "")  # dynamic

        # loose documentation
        if "'param'" in params:
            params = params.replace("'param'", "param")  # Q&D

        # .. function:: ussl.wrap_socket(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=CERT_NONE, ca_certs=None, do_handshake=True)
        params = params.replace("cert_reqs=CERT_NONE", "cert_reqs=None")  # Q&D

        if "dhcp" in params:
            # network.rst method:: WLANWiPy.ifconfig(if_id=0, config=['dhcp' or configtuple])
            params = params.replace(
                "='dhcp' or configtuple: Optional[Any]", ": Union[str,Tuple]='dhcp'"
            )
        if "'pgm'" in params:
            # network.rst .. method:: CC3K.patch_program('pgm')
            params = params.replace("'pgm')", "cmd:str ,/)")

        if "block_device" in params:
            params = params.replace("block_device or path", "block_device_or_path")

        # ifconfig
        params = params.replace(
            "(ip, subnet, gateway, dns):Optional[Any]", "config: Optional[Tuple]"
        )  # Q&D

        # illegal keywords
        if "lambda" in params:
            params = params.replace("lambda", "lambda_fn")

        # formatting
        return params

    def output_docstring(self, docstr):
        # if len(docstr) > 0:
        self.writeln(f'{self.indent}"""')
        for l in docstr:
            self.writeln(f"{self.indent}{l}")
        self.writeln(f'{self.indent}"""')

    def output_class_hdr(self, name: str, params: str, docstr: List[str]):
        # hack assume no classes in classes  or functions in functions
        self.leave_class()

        # write a class header
        self.writeln(f"{self.indent}class {name}:")

        self.updent()
        self.output_docstring(docstr)

        if len(params) > 0:
            # only output init when there is info
            self.writeln(f"{self.indent}def __init__(self, {params} -> None:")
            self.updent()
            self.writeln(f"{self.indent}...\n")
            self.dedent()
        self.current_class = name
        # helper to keep track of indentation
        self.classes.append(name.lower())

    def parse_toc(self, n: int):
        "process table of content with additional rst files, and add / include them in the current module"
        n += 1  # skip one line
        n, toctree = self.read_textblock(n)
        # cleanup toctree
        toctree = [x.strip() for x in toctree if f"{self.current_module}." in x]

        for file in toctree:
            self.read_file(f"micropython/docs/library/{file.strip()}")
            self.parse()

    def parse(self, depth: int = 0):
        self.depth = depth
        # todo : replace by while and n+=1
        # or stop using self.to store state
        # for n in range(0, len(self.rst_text)):
        n = 0
        while n < len(self.rst_text):
            line = self.rst_text[n]
            #    self.writeln(">"+line)

            if re.search(r"\.\. module::", line):
                self.log(f"# {line.rstrip()}")
                this_module = line.split(self.sep)[-1].strip()
                self.writeln(f"# origin: {self.filename}\n# {self.source_tag}")
                # get module docstring
                self.current_module = this_module
                self.current_function = self.current_class = ""
                n, docstr = self.read_textblock(n)
                self.output_docstring(docstr)

            elif re.search(r"\.\. currentmodule::", line):
                n += 1
                self.log(f"# {line.rstrip()}")
                this_module = line.split(self.sep)[-1].strip()
                self.log(f"# currentmodule:: {this_module}")
                self.current_module = this_module
                self.current_function = self.current_class = ""
                # todo: check if same module
                # todo: read first block and do something with it

            elif re.search(r"\.\. function::", line):
                self.log(f"# {line.rstrip()}")
                this_function = line.split(self.sep)[-1].strip()
                ret_type = "Any"
                n, docstr = self.read_textblock(n)
                name, params = this_function.split("(", maxsplit=1)
                self.current_function = name
                if name not in ("classmethod", "staticmethod"):
                    # ussl docstring uses a prefix
                    # remove module name from the start of the function name
                    if name.startswith(f"{self.current_module}."):
                        name = name[len(f"{self.current_module}.") :]
                    # todo: parse return type from docstring
                    # fixup optional [] variables
                    params = self.fix_parameters(params)
                    # assume functions in classes
                    self.leave_class()
                    # if function name is the same as the module
                    # then this is probably documenting a class ()
                    # FIXME: usocket socket
                    # if self.current_module in (name, f"u{name}"):
                    if name in (self.current_module, f"u{self.current_module}"):
                        if self.verbose or self.__debug:
                            self.writeln(f"{self.indent}# ..................................")
                            self.writeln(f"{self.indent}# 'Promote' function to class: {name}")
                        # write a class header
                        self.output_class_hdr(name, params, docstr)
                    else:
                        self.writeln(f"{self.indent}def {name}({params} -> {ret_type}:")
                        self.updent()
                        self.output_docstring(docstr)
                        self.writeln(f"{self.indent}...\n\n")
                        self.dedent()

            elif re.search(r"\.\. class::?", line):
                # todo: Docbug # .. _class: Poll micropython\docs\library\uselect.rst
                self.log(f"# {line.rstrip()}")
                this_class = line.split(self.sep)[-1].strip()
                name = this_class
                params = ""
                if "(" in this_class:
                    name, params = this_class.split("(", 2)
                self.current_class = name
                self.current_function = ""
                # remove module name from the start of the class name
                if name.startswith(f"{self.current_module}."):
                    name = name[len(f"{self.current_module}.") :]
                self.log(f"# class:: {name}")
                # fixup optional [] variables
                params = self.fix_parameters(params)
                n, docstr = self.read_textblock(n)
                if any(":noindex:" in line for line in docstr):
                    # if the class docstring contains ':noindex:' on any line then skip
                    self.log(f"# Skip :noindex: class {name}")
                else:
                    # write a class header
                    self.output_class_hdr(name, params, docstr)

            elif (
                re.search(r"\.\. method::", line)
                or re.search(r"\.\. staticmethod::", line)
                or re.search(r"\.\. classmethod::", line)
            ):
                name = ""
                this_method = ""
                params = ")"
                ## py:staticmethod  - py:classmethod - py:decorator
                # ref: https://sphinx-tutorial.readthedocs.io/cheatsheet/
                self.log(f"# {line.rstrip()}")
                this_method = line.split(self.sep)[1].strip()
                ret_type = "Any"
                try:
                    name, params = this_method.split("(", 1)  # split methodname from params
                except ValueError:
                    name = this_method
                self.current_function = name
                # self.writeln(f"# method:: {name}")
                # fixup optional [] parameters and other notations
                params = self.fix_parameters(params)
                if "." in name:
                    # todo: deal with longer / deeper classes
                    class_name = name.split(".")[0]
                else:
                    # if nothing specified lets assume part of current class
                    class_name = self.current_class
                name = name.split(".")[-1]  # Take only the last part from Pin.toggle

                if name == "__init__" and self.no_explicit_init:
                    # init is hardcoded , do not add it twice (? or dedent to add it as an overload ?)
                    # FIXME: ucryptolib aes.__init__(key, mode, [IV])
                    n += 1
                else:
                    # todo: check if the class statement has already been started

                    if (
                        not class_name in self.current_class
                        and not class_name.lower() in self.current_class.lower()
                    ):
                        self.output_class_hdr(class_name, "", [])
                    n, docstr = self.read_textblock(n)

                    # todo: parse return type from docstring
                    if name == "__init__":
                        # explicitly documented __init__ ( only a few classes)
                        self.writeln(f"{self.indent}def {name}(self, {params} -> None:")
                        ...
                    elif re.search(r"\.\. classmethod::", line):
                        self.writeln(f"{self.indent}@classmethod")
                        self.writeln(f"{self.indent}def {name}(cls, {params} -> {ret_type}:")
                        ...
                    elif re.search(r"\.\. staticmethod::", line):
                        self.writeln(f"{self.indent}@staticmethod")
                        self.writeln(f"{self.indent}def {name}({params} -> {ret_type}:")
                        ...
                    else:
                        self.writeln(f"{self.indent}def {name}(self, {params} -> {ret_type}:")
                    self.updent()
                    self.output_docstring(docstr)
                    self.writeln(f"{self.indent}...\n")
                    self.dedent()

            elif re.search(r"\.\. exception::", line):
                self.log(f"# {line.rstrip()}")
                n += 1
                name = line.split(self.sep)[1].strip()
                if "." in name:
                    name = name.split(".")[-1]  # Take only the last part from Pin.toggle
                self.writeln(f"{self.indent}class {name}(BaseException) : ...")

                # class Exception(BaseException): ...

            elif re.search(r"\.\. data::", line):
                self.log(f"# {line.rstrip()}")
                n += 1
                # todo: find a way to reliably add Constants at the correct level
                # Note : makestubs has no issue with this

                # self.updent()
                # # BUG: check if this is the correct identation for root level ?
                # this_const = line.split(self.sep)[-1].strip()
                # name = this_const.split(".")[1]  # Take only the last part from Pin.toggle
                # type = "Any"
                # # deal with documentation wildcards
                # if "*" in name:
                #     self.log(f"# fix constant {name}")
                #     name = f"# {name}"

                # self.writeln(f"{self.indent}{name} : {type} = None")
                # self.dedent()

            elif re.search(r"\.\. toctree::", line):
                self.log(f"# {line.rstrip()}")
                self.parse_toc(n)
                # reset to done
                self.rst_text = []
                n = 1
            elif re.search(r"\.\. \w+::", line):
                #
                self.log(f"# {line.rstrip()}")
                print(_red(line.rstrip()))
                n += 1
            else:
                # NOTHING TO SEE HERE , MOVE ON
                n += 1


def generate_from_rst(rst_folder: Path, dst_folder: Path, v_tag: str, black=True) -> int:
    if not dst_folder.exists():
        dst_folder.mkdir(parents=True)
    # no index, and module.xxx.rst is included in module.py
    files = [f for f in rst_folder.glob("*.rst") if f.stem != "index" and "." not in f.stem]
    for file in files:
        reader = RSTReader(v_tag)
        reader.read_file(file)
        reader.parse()
        reader.write_file((dst_folder / file.name).with_suffix(".py"))
        del reader

    if black:
        try:
            cmd = f"black {dst_folder.as_posix()}"
            result = subprocess.run(cmd, capture_output=False, check=True)
            if result.returncode != 0:
                raise Exception(result.stderr.decode("utf-8"))
        except subprocess.SubprocessError:
            print(_red("some of the files are not in a proper format"))

    return len(files)


if __name__ == "__main__":
    base_path = "micropython"
    v_tag = git.get_tag(base_path)
    if not v_tag:
        # if we can't find a tag , bail
        raise ValueError

    rst_folder = Path(base_path) / "docs" / "library"
    dst_folder = Path("generated/micropython") / flat_version(v_tag)
    generate_from_rst(rst_folder, dst_folder, v_tag)

# todo
# constants
# usocket : class is defined twice - discontinuous documentation

# todo: .. exception:: IndexError

# todo: documentation contains  repeated vars with the same identation
# .. data:: IPPROTO_UDP
#           IPPROTO_TCP

# todo: cleanup '(self, ) -> Any:' -> (self) -> Any:'

# Done

# Duplicate __init__ FIXME: ucryptolib aes.__init__(key, mode, [IV])

# ucollection   : docs incorrectly states classes as functions --> upstream

# cmd = 'black generated/micropython/v1.5.2'
# subprocess.run(cmd, capture_output=False, check=True)
