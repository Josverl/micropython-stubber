# read text
from typing import List, Tuple
from pathlib import Path


class RSTReader:
    def __init__(self):
        self.sep = "::"
        self.this_module = ""
        self.current_module = ""
        self.filename = ""
        self.depth = 0
        self.rst_text: List[str] = []
        self.max_line = 0
        self.output: List[str] = []
        self.verbose = False
        self.source_tag = "v1.16"
        self.target = ".py"  # py/pyi
        self.in_class: List[str] = []

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

    def write_file(self, filename: Path) -> bool:
        try:
            print(f" - Writing to: {filename}")
            with open(filename, mode="w", encoding="utf8") as file:
                file.writelines(self.output)
            return True
        except OSError as e:
            print(e)
            return False

    def read_textblock(self, n: int) -> Tuple[int, List[str]]:
        if n >= len(self.rst_text):
            raise IndexError
        block: List[str] = []
        n += 1  # advance over current line
        try:
            while (
                n < len(self.rst_text)
                and not self.rst_text[n].startswith("..")  # function / method
                and not self.rst_text[min(n + 1, self.max_line)].startswith("--")  # Heading --
                and not self.rst_text[min(n + 1, self.max_line)].startswith("==")  # Heading ==
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
        return (n + 1, block)

    def fix_parameters(self, params: str):
        "change notation issues into a supported version"
        # multiple optionals
        # # .. method:: Servo.angle([angle, time=0])
        params = params.replace("[angle, time=0]", "[angle], time=0")
        # sublist parameters are not supported in python 3
        # method:: ADC.read_timed_multi((adcx, adcy, ...), (bufx, bufy, ...), timer)
        params = params.replace("(adcx, adcy, ...), (bufx, bufy, ...)", "adcs, bufs")
        params = params.replace("", "")
        params = params.replace("", "")

        # change [x] --> x:Optional[Any]
        params = params.replace("[", "")
        params = params.replace("]]", "")  # Q&D Hack-complex nesting
        params = params.replace("]", ":Optional[Any]")
        # change \* --> *
        params = params.replace("\\*", "*")
        # ... not allowed in .py
        if self.target == ".py":
            params = params.replace("*, ...", "*args")
            params = params.replace("...", "*args")
        # todo: change or remove value hints (...|....)
        # params = params.replace("pins=(SCK, MOSI, MISO)", "")  # Q&D

        # todo:  machine.IDLE --> IDLE      - module level
        params = params.replace("machine.", "")  # Q&D
        # todo:  SPI.MSB --> MSB      - class level
        params = params.replace("SPI.", "")  # Q&D
        params = params.replace("Timer.", "")  # Q&D

        # loose documentation
        params = params.replace("'param'", "param")  # Q&D
        # .. function:: ussl.wrap_socket(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=CERT_NONE, ca_certs=None, do_handshake=True)
        params = params.replace("cert_reqs=CERT_NONE", "cert_reqs=None")  # Q&D

        # ifconfig
        params = params.replace(
            "(ip, subnet, gateway, dns):Optional[Any]", "config:Optional[Tuple]"
        )  # Q&D

        return params

    def output_docstring(self, docstr):
        # if len(docstr) > 0:
        self.writeln(f'{self.indent}"""')
        for l in docstr:
            self.writeln(f"{self.indent}{l}")
        self.writeln(f'{self.indent}"""')

    def output_class_hdr(self, name: str, params: str, docstr: List[str]):
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
        # helper to keep track of indentation
        self.in_class.append(name.lower())

    def parse(self, depth: int = 0):
        self.depth = depth
        # todo : replace by while and n+=1
        # or stop using self.to store state
        # for n in range(0, len(self.rst_text)):
        n = 0
        while n < len(self.rst_text):
            line = self.rst_text[n]
            #    self.writeln(">"+line)

            if line.startswith(".. module::"):
                self.log(f"# {line.rstrip()}")
                this_module = line.split(self.sep)[-1].strip()
                self.writeln(f"# origin: {self.filename}\n# {self.source_tag}")
                # get module docstring
                self.current_module = this_module
                n, docstr = self.read_textblock(n)
                self.output_docstring(docstr)
                self.writeln("\nfrom typing import Any, Optional, Union, Tuple\n")

            if line.startswith(".. currentmodule::"):
                self.log(f"# {line.rstrip()}")
                this_module = line.split(self.sep)[-1].strip()
                self.log(f"# currentmodule:: {this_module}")
                self.current_module = this_module
                # todo: check if same module
                # todo: read first block and do something with it

            elif line.startswith(".. function::"):
                self.log(f"# {line.rstrip()}")
                this_function = line.split(self.sep)[-1].strip()
                ret_type = "Any"
                n, docstr = self.read_textblock(n)
                name, params = this_function.split("(", 2)
                # ussl docstring uses a prefix
                # remove module name from the start of the function name
                if name.startswith(f"{self.current_module}."):
                    name = name[len(f"{self.current_module}.") :]

                # todo: parse return type from docstring
                # fixup optional [] variables
                params = self.fix_parameters(params)

                # if function name is the same as the module
                # then this is probably documenting a class ()
                # usocket socket
                if self.current_module in (name, f"u{name}"):
                    # write a class header
                    self.output_class_hdr(name, params, docstr)
                else:
                    self.writeln(f"{self.indent}def {name}({params} ->{ret_type}:")
                    self.updent()
                    self.output_docstring(docstr)
                    self.writeln(f"{self.indent}...\n")
                    self.dedent()

            elif line.startswith(".. class::"):
                self.log(f"# {line.rstrip()}")
                self.log(f"# {line}")
                this_class = line.split(self.sep)[-1].strip()
                name = this_class
                params = ""
                if "(" in this_class:
                    name, params = this_class.split("(", 2)
                # remove module name from the start of the class name
                if name.startswith(f"{self.current_module}."):
                    name = name[len(f"{self.current_module}.") :]
                self.log(f"# class:: {name}")
                # fixup optional [] variables
                params = self.fix_parameters(params)
                n, docstr = self.read_textblock(n)

                # write a class header
                self.output_class_hdr(name, params, docstr)

            # todo: detect end of class to dedent

            # elif line.startswith("Constants"):
            #     # self.dedent()
            #     self.log(f"# Constant: ~end of class dedent to {self.depth}")

            elif line.startswith(".. method::"):
                self.log(f"# {line.rstrip()}")
                this_method = line.split(self.sep)[-1].strip()
                ret_type = "Any"
                name, params = this_method.split("(", 1)  # split methodname from params
                # self.writeln(f"# method:: {name}")
                # fixup optional [] variables
                params = self.fix_parameters(params)
                # todo: deal with longer / deeper classes
                class_name = name.split(".")[0]
                name = name.split(".")[-1]  # Take only the last part from Pin.toggle
                # todo: check if the class statement has already been started
                if class_name.lower() not in self.in_class:
                    self.output_class_hdr(class_name, "", [])
                n, docstr = self.read_textblock(n)

                # todo: parse return type from docstring

                self.writeln(f"{self.indent}def {name}(self, {params} -> {ret_type}:")
                self.updent()
                self.output_docstring(docstr)
                self.writeln(f"{self.indent}...\n")
                self.dedent()

            elif line.startswith(".. data::"):
                self.log(f"# {line.rstrip()}")
                # todo: find a way to reliably add Constants at the correct level
                # Note : makestubs has no issue with this

                # self.updent()
                # # BUG: check if this is the correct identation for root level ?
                # this_const = line.split(self.sep)[-1].strip()
                # name = this_const.split(".")[-1]  # Take only the last part from Pin.toggle
                # type = "Any"
                # # deal with documentation wildcards
                # if "*" in name:
                #     self.log(f"# fix constant {name}")
                #     name = f"# {name}"

                # self.writeln(f"{self.indent}{name} : {type} = None")
                # self.dedent()

                # todo: documentation contains  repeated vars with the same identation
                # .. data:: IPPROTO_UDP
                #           IPPROTO_TCP

            elif line.startswith(".. toctree::"):
                self.log(f"# {line.rstrip()}")
                # process additional files
                n += 1  # skip one line
                n, toctree = self.read_textblock(n)
                # cleanup toctree
                toctree = [x.strip() for x in toctree if f"{self.this_module}." in x]

                for file in toctree:
                    reader.read_file(f"micropython/docs/library/{file.strip()}")
                    reader.parse()
                # reset to done
                self.rst_text = []
                n = 0
            # todo: errorclasses

            elif line.startswith(".."):
                self.log(f"# {line.rstrip()}")
            n += 1


files = [
    "_thread.rst",
    "btree.rst",
    "builtins.rst",
    "cmath.rst",
    "esp.rst",
    "esp32.rst",
    "framebuf.rst",
    "gc.rst",
    #    "index.rst",
    "lcd160cr.rst",
    "machine.rst",
    "math.rst",
    "micropython.rst",
    "network.rst",
    "pyb.rst",
    "rp2.rst",
    "uarray.rst",
    "uasyncio.rst",
    "ubinascii.rst",
    "ubluetooth.rst",
    "ucollections.rst",
    "ucryptolib.rst",
    "uctypes.rst",
    "uerrno.rst",
    "uhashlib.rst",
    "uheapq.rst",
    "uio.rst",
    "ujson.rst",
    "uos.rst",
    "ure.rst",
    "uselect.rst",
    "usocket.rst",
    "ussl.rst",
    "ustruct.rst",
    "usys.rst",
    "utime.rst",
    "uzlib.rst",
    "wipy.rst",
]


# reader.read_file(f"micropython/docs/library/machine.rst")
# reader.parse()


# files = [
#     "usocket.rst",
#     #     "btree.rst",
#     #     "machine.rst",
# ]
rst_folder = Path("micropython/docs/library")
dest_folder = Path("generated/micropython") / "v1_16"
if not dest_folder.exists():
    dest_folder.mkdir(parents=True)

for file in files:
    reader = RSTReader()
    reader.read_file(rst_folder / file)
    reader.parse()
    reader.write_file((dest_folder / file).with_suffix(".py"))
