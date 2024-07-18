"""
Create stubs for (all) modules on a MicroPython board.

    This variant of the createstubs.py script is optimized for use on very-low-memory devices.
    Note: this version has undergone limited testing.
    
    1) reads the list of modules from a text file `modulelist.txt` that should be uploaded to the device.
    2) stored the already processed modules in a text file `modulelist.done` 
    3) process the modules in the database:
        - stub the module
        - update the modulelist.done file
        - reboots the device if it runs out of memory
    4) creates the modules.json

    If that cannot be found then only a single module (micropython) is stubbed.
    In order to run this on low-memory devices two additional steps are recommended: 
    - minification, using python-minifierto reduce overall size, and remove logging overhead.
    - cross compilation, using mpy-cross, to avoid the compilation step on the micropython device 


This variant was generated from createstubs.py by micropython-stubber v1.23.2
"""

# Copyright (c) 2019-2024 Jos Verlinde

import gc
import os
import sys
from time import sleep

try:
    from ujson import dumps
except:
    from json import dumps

try:
    from machine import reset  # type: ignore
except ImportError:
    pass

try:
    from collections import OrderedDict
except ImportError:
    from ucollections import OrderedDict  # type: ignore

__version__ = "v1.23.2"
version_str = __version__.rsplit(".", 1)[0]
ENOENT = 2
_MAX_CLASS_LEVEL = 2  # Max class nesting
LIBS = ["lib", "/lib", "/sd/lib", "/flash/lib", "."]


# our own logging module to avoid dependency on and interfering with logging module
class logging:
    # DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    level = INFO
    prnt = print

    @staticmethod
    def getLogger(name):
        return logging()

    @classmethod
    def basicConfig(cls, level):
        cls.level = level

    # def debug(self, msg):
    #     if self.level <= logging.DEBUG:
    #         self.prnt("DEBUG :", msg)

    def info(self, msg):
        if self.level <= logging.INFO:
            self.prnt("INFO  :", msg)

    def warning(self, msg):
        if self.level <= logging.WARNING:
            self.prnt("WARN  :", msg)

    def error(self, msg):
        if self.level <= logging.ERROR:
            self.prnt("ERROR :", msg)


log = logging.getLogger("stubber")
logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)


class Stubber:
    "Generate stubs for modules in firmware"

    def __init__(self, path: str = None, firmware_id: str = None):  # type: ignore
        try:
            if os.uname().release == "1.13.0" and os.uname().version < "v1.13-103":  # type: ignore
                raise NotImplementedError("MicroPython 1.13.0 cannot be stubbed")
        except AttributeError:
            pass  # Allow testing on CPython 3.11
        self.info = _info()
        log.info("Port: {}".format(self.info["port"]))
        log.info("Board: {}".format(self.info["board"]))
        gc.collect()
        if firmware_id:
            self._fwid = firmware_id.lower()
        else:
            if self.info["family"] == "micropython":
                self._fwid = "{family}-v{version}-{port}-{board}".format(**self.info).rstrip("-")
            else:
                self._fwid = "{family}-v{version}-{port}".format(**self.info)
        self._start_free = gc.mem_free()  # type: ignore

        if path:
            if path.endswith("/"):
                path = path[:-1]
        else:
            path = get_root()

        self.path = "{}/stubs/{}".format(path, self.flat_fwid).replace("//", "/")
        # log.debug(self.path)
        try:
            ensure_folder(path + "/")
        except OSError:
            log.error("error creating stub folder {}".format(path))
        self.problematic = [
            "upip",
            "upysh",
            "webrepl_setup",
            "http_client",
            "http_client_ssl",
            "http_server",
            "http_server_ssl",
        ]
        self.excluded = [
            "webrepl",
            "_webrepl",
            "port_diag",
            "example_sub_led.py",
            "example_pub_button.py",
        ]
        # there is no option to discover modules from micropython, list is read from an external file.
        self.modules = []  # type: list[str]
        self._json_name = None
        self._json_first = False

    def get_obj_attributes(self, item_instance: object):
        "extract information of the objects members and attributes"
        # name_, repr_(value), type as text, item_instance
        _result = []
        _errors = []
        # log.debug("get attributes {} {}".format(repr(item_instance), item_instance))
        for name in dir(item_instance):
            if name.startswith("__") and not name in self.modules:
                continue
            # log.debug("get attribute {}".format(name))
            try:
                val = getattr(item_instance, name)
                # name , item_repr(value) , type as text, item_instance, order
                # log.debug("attribute {}:{}".format(name, val))
                try:
                    type_text = repr(type(val)).split("'")[1]
                except IndexError:
                    type_text = ""
                if type_text in {"int", "float", "str", "bool", "tuple", "list", "dict"}:
                    order = 1
                elif type_text in {"function", "method"}:
                    order = 2
                elif type_text in ("class"):
                    order = 3
                else:
                    order = 4
                _result.append((name, repr(val), repr(type(val)), val, order))
            except AttributeError as e:
                _errors.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(name, item_instance, e))
            except MemoryError as e:
                print("MemoryError: {}".format(e))
                sleep(1)
                reset()

        # remove internal __
        # _result = sorted([i for i in _result if not (i[0].startswith("_"))], key=lambda x: x[4])
        _result = sorted([i for i in _result if not (i[0].startswith("__"))], key=lambda x: x[4])
        gc.collect()
        return _result, _errors

    def add_modules(self, modules):
        "Add additional modules to be exported"
        self.modules = sorted(set(self.modules) | set(modules))

    def create_all_stubs(self):
        "Create stubs for all configured modules"
        log.info("Start micropython-stubber {} on {}".format(__version__, self._fwid))
        self.report_start()
        gc.collect()
        for module_name in self.modules:
            self.create_one_stub(module_name)
        self.report_end()
        log.info("Finally done")

    def create_one_stub(self, module_name: str):
        if module_name in self.problematic:
            log.warning("Skip module: {:<25}        : Known problematic".format(module_name))
            return False
        if module_name in self.excluded:
            log.warning("Skip module: {:<25}        : Excluded".format(module_name))
            return False

        file_name = "{}/{}.pyi".format(self.path, module_name.replace(".", "/"))
        gc.collect()
        result = False
        try:
            result = self.create_module_stub(module_name, file_name)
        except OSError:
            return False
        gc.collect()
        return result

    def create_module_stub(self, module_name: str, file_name: str = None) -> bool:  # type: ignore
        """Create a Stub of a single python module

        Args:
        - module_name (str): name of the module to document. This module will be imported.
        - file_name (Optional[str]): the 'path/filename.pyi' to write to. If omitted will be created based on the module name.
        """
        if file_name is None:
            fname = module_name.replace(".", "_") + ".pyi"
            file_name = self.path + "/" + fname
        else:
            fname = file_name.split("/")[-1]

        if "/" in module_name:
            # for nested modules
            module_name = module_name.replace("/", ".")

        # import the module (as new_module) to examine it
        new_module = None
        try:
            new_module = __import__(module_name, None, None, ("*"))
            m1 = gc.mem_free()  # type: ignore
            log.info("Stub module: {:<25} to file: {:<70} mem:{:>5}".format(module_name, fname, m1))

        except ImportError:
            # log.debug("Skip module: {:<25} {:<79}".format(module_name, "Module not found."))
            return False

        # Start a new file
        ensure_folder(file_name)
        with open(file_name, "w") as fp:
            info_ = str(self.info).replace("OrderedDict(", "").replace("})", "}")
            s = '"""\nModule: \'{0}\' on {1}\n"""\n# MCU: {2}\n# Stubber: {3}\n'.format(module_name, self._fwid, info_, version_str)
            fp.write(s)
            fp.write("from __future__ import annotations\nfrom typing import Any, Generator\nfrom _typeshed import Incomplete\n\n")
            self.write_object_stub(fp, new_module, module_name, "")

        self.report_add(module_name, file_name)

        if module_name not in {"os", "sys", "logging", "gc"}:
            # try to unload the module unless we use it
            try:
                del new_module
            except (OSError, KeyError):  # lgtm [py/unreachable-statement]
                log.warning("could not del new_module")
            # do not try to delete from sys.modules - most times it does not work anyway
        gc.collect()
        return True

    def write_object_stub(self, fp, object_expr: object, obj_name: str, indent: str, in_class: int = 0):
        "Write a module/object stub to an open file. Can be called recursive."
        gc.collect()
        if object_expr in self.problematic:
            log.warning("SKIPPING problematic module:{}".format(object_expr))
            return

        # # log.debug("DUMP    : {}".format(object_expr))
        items, errors = self.get_obj_attributes(object_expr)

        if errors:
            log.error(errors)

        for item_name, item_repr, item_type_txt, item_instance, _ in items:
            # name_, repr_(value), type as text, item_instance, order
            if item_name in ["classmethod", "staticmethod", "BaseException", "Exception"]:
                # do not create stubs for these primitives
                continue
            if item_name[0].isdigit():
                log.warning("NameError: invalid name {}".format(item_name))
                continue
            # Class expansion only on first 3 levels (bit of a hack)
            if (
                item_type_txt == "<class 'type'>"
                and len(indent) <= _MAX_CLASS_LEVEL * 4
                # and not obj_name.endswith(".Pin")
                # avoid expansion of Pin.cpu / Pin.board to avoid crashes on most platforms
            ):
                # log.debug("{0}class {1}:".format(indent, item_name))
                superclass = ""
                is_exception = (
                    item_name.endswith("Exception")
                    or item_name.endswith("Error")
                    or item_name
                    in [
                        "KeyboardInterrupt",
                        "StopIteration",
                        "SystemExit",
                    ]
                )
                if is_exception:
                    superclass = "Exception"
                s = "\n{}class {}({}):\n".format(indent, item_name, superclass)
                # s += indent + "    ''\n"
                if is_exception:
                    s += indent + "    ...\n"
                    fp.write(s)
                    continue
                # write classdef
                fp.write(s)
                # first write the class literals and methods
                # log.debug("# recursion over class {0}".format(item_name))
                self.write_object_stub(
                    fp,
                    item_instance,
                    "{0}.{1}".format(obj_name, item_name),
                    indent + "    ",
                    in_class + 1,
                )
                # end with the __init__ method to make sure that the literals are defined
                # Add __init__
                s = indent + "    def __init__(self, *argv, **kwargs) -> None:\n"
                s += indent + "        ...\n\n"
                fp.write(s)
            elif any(word in item_type_txt for word in ["method", "function", "closure"]):
                # log.debug("# def {1} function/method/closure, type = '{0}'".format(item_type_txt, item_name))
                # module Function or class method
                # will accept any number of params
                # return type Any/Incomplete
                ret = "Incomplete"
                first = ""
                # Self parameter only on class methods/functions
                if in_class > 0:
                    first = "self, "
                # class method - add function decoration
                if "bound_method" in item_type_txt or "bound_method" in item_repr:
                    s = "{}@classmethod\n".format(indent) + "{}def {}(cls, *args, **kwargs) -> {}:\n".format(indent, item_name, ret)
                else:
                    s = "{}def {}({}*args, **kwargs) -> {}:\n".format(indent, item_name, first, ret)
                s += indent + "    ...\n\n"
                fp.write(s)
                # log.debug("\n" + s)
            elif item_type_txt == "<class 'module'>":
                # Skip imported modules
                # fp.write("# import {}\n".format(item_name))
                pass

            elif item_type_txt.startswith("<class '"):
                t = item_type_txt[8:-2]
                s = ""

                if t in ("str", "int", "float", "bool", "bytearray", "bytes"):
                    # known type: use actual value
                    # s = "{0}{1} = {2} # type: {3}\n".format(indent, item_name, item_repr, t)
                    s = "{0}{1}: {3} = {2}\n".format(indent, item_name, item_repr, t)
                elif t in ("dict", "list", "tuple"):
                    # dict, list , tuple: use empty value
                    ev = {"dict": "{}", "list": "[]", "tuple": "()"}
                    # s = "{0}{1} = {2} # type: {3}\n".format(indent, item_name, ev[t], t)
                    s = "{0}{1}: {3} = {2}\n".format(indent, item_name, ev[t], t)
                else:
                    # something else
                    if t in ("object", "set", "frozenset", "Pin", "generator"):  # "FileIO"
                        # https://docs.python.org/3/tutorial/classes.html#item_instance-objects
                        # use these types for the attribute
                        if t == "generator":
                            t = "Generator"
                        s = "{0}{1}: {2} ## = {4}\n".format(indent, item_name, t, item_type_txt, item_repr)
                    else:
                        # Requires Python 3.6 syntax, which is OK for the stubs/pyi
                        t = "Incomplete"
                        if " at " in item_repr:
                            item_repr = item_repr.split(" at ")[0] + " at ...>"
                        if " at " in item_repr:
                            item_repr = item_repr.split(" at ")[0] + " at ...>"
                        s = "{0}{1}: {2} ## {3} = {4}\n".format(indent, item_name, t, item_type_txt, item_repr)
                fp.write(s)
                # log.debug("\n" + s)
            else:
                # keep only the name
                # log.debug("# all other, type = '{0}'".format(item_type_txt))
                fp.write("# all other, type = '{0}'\n".format(item_type_txt))

                fp.write(indent + item_name + " # type: Incomplete\n")

        # del items
        # del errors
        # try:
        #     del item_name, item_repr, item_type_txt, item_instance  # type: ignore
        # except (OSError, KeyError, NameError):
        #     pass

    @property
    def flat_fwid(self):
        "Turn _fwid from 'v1.2.3' into '1_2_3' to be used in filename"
        s = self._fwid
        # path name restrictions
        chars = " .()/\\:$"
        for c in chars:
            s = s.replace(c, "_")
        return s

    def clean(self, path: str = None):  # type: ignore
        "Remove all files from the stub folder"
        if path is None:
            path = self.path
        log.info("Clean/remove files in folder: {}".format(path))
        try:
            os.stat(path)  # TEMP workaround mpremote listdir bug -
            items = os.listdir(path)
        except (OSError, AttributeError):
            # os.listdir fails on unix
            return
        for fn in items:
            item = "{}/{}".format(path, fn)
            try:
                os.remove(item)
            except OSError:
                try:  # folder
                    self.clean(item)
                    os.rmdir(item)
                except OSError:
                    pass

    def report_start(self, filename: str = "modules.json"):
        """Start a report of the modules that have been stubbed
        "create json with list of exported modules"""
        self._json_name = "{}/{}".format(self.path, filename)
        self._json_first = True
        ensure_folder(self._json_name)
        log.info("Report file: {}".format(self._json_name))
        gc.collect()
        try:
            # write json by node to reduce memory requirements
            with open(self._json_name, "w") as f:
                f.write("{")
                f.write(dumps({"firmware": self.info})[1:-1])
                f.write(",\n")
                f.write(dumps({"stubber": {"version": version_str}, "stubtype": "firmware"})[1:-1])
                f.write(",\n")
                f.write('"modules" :[\n')

        except OSError as e:
            log.error("Failed to create the report.")
            self._json_name = None
            raise e

    def report_add(self, module_name: str, stub_file: str):
        "Add a module to the report"
        # write json by node to reduce memory requirements
        if not self._json_name:
            raise Exception("No report file")
        try:
            with open(self._json_name, "a") as f:
                if not self._json_first:
                    f.write(",\n")
                else:
                    self._json_first = False
                line = '{{"module": "{}", "file": "{}"}}'.format(module_name, stub_file.replace("\\", "/"))
                f.write(line)

        except OSError:
            log.error("Failed to create the report.")

    def report_end(self):
        if not self._json_name:
            raise Exception("No report file")
        with open(self._json_name, "a") as f:
            f.write("\n]}")
        # is used as sucess indicator
        log.info("Path: {}".format(self.path))


def ensure_folder(path: str):
    "Create nested folders if needed"
    i = start = 0
    while i != -1:
        i = path.find("/", start)
        if i != -1:
            p = path[0] if i == 0 else path[:i]
            # p = partial folder
            try:
                _ = os.stat(p)
            except OSError as e:
                # folder does not exist
                if e.args[0] == ENOENT:
                    try:
                        os.mkdir(p)
                    except OSError as e2:
                        log.error("failed to create folder {}".format(p))
                        raise e2
        # next level deep
        start = i + 1


def _build(s):
    # extract build from sys.version or os.uname().version if available
    # sys.version: 'MicroPython v1.23.2-preview.6.g3d0b6276f'
    # sys.implementation.version: 'v1.13-103-gb137d064e'
    if not s:
        return ""
    s = s.split(" on ", 1)[0] if " on " in s else s
    if s.startswith("v"):
        if not "-" in s:
            return ""
        b = s.split("-")[1]
        return b
    if not "-preview" in s:
        return ""
    b = s.split("-preview")[1].split(".")[1]
    return b


def _info():  # type:() -> dict[str, str]
    try:
        fam = sys.implementation[0]  # type: ignore
    except TypeError:
        # testing on CPython 3.11
        fam = sys.implementation.name

    info = OrderedDict(
        {
            "family": fam,
            "version": "",
            "build": "",
            "ver": "",
            "port": sys.platform,  # port: esp32 / win32 / linux / stm32
            "board": "UNKNOWN",
            "cpu": "",
            "mpy": "",
            "arch": "",
        }
    )
    # change port names to be consistent with the repo
    if info["port"].startswith("pyb"):
        info["port"] = "stm32"
    elif info["port"] == "win32":
        info["port"] = "windows"
    elif info["port"] == "linux":
        info["port"] = "unix"
    try:
        info["version"] = version_str(sys.implementation.version)  # type: ignore
    except AttributeError:
        pass
    try:
        _machine = sys.implementation._machine if "_machine" in dir(sys.implementation) else os.uname().machine  # type: ignore
        # info["board"] = "with".join(_machine.split("with")[:-1]).strip()
        info["board"] = _machine
        info["cpu"] = _machine.split("with")[-1].strip()
        info["mpy"] = (
            sys.implementation._mpy  # type: ignore
            if "_mpy" in dir(sys.implementation)
            else sys.implementation.mpy if "mpy" in dir(sys.implementation) else ""  # type: ignore
        )
    except (AttributeError, IndexError):
        pass
    info["board"] = get_boardname()

    try:
        if "uname" in dir(os):  # old
            # extract build from uname().version if available
            info["build"] = _build(os.uname()[3])  # type: ignore
            if not info["build"]:
                # extract build from uname().release if available
                info["build"] = _build(os.uname()[2])  # type: ignore
        elif "version" in dir(sys):  # new
            # extract build from sys.version if available
            info["build"] = _build(sys.version)
    except (AttributeError, IndexError, TypeError):
        pass
    # avoid  build hashes
    # if info["build"] and len(info["build"]) > 5:
    #     info["build"] = ""

    if info["version"] == "" and sys.platform not in ("unix", "win32"):
        try:
            u = os.uname()  # type: ignore
            info["version"] = u.release
        except (IndexError, AttributeError, TypeError):
            pass
    # detect families
    for fam_name, mod_name, mod_thing in [
        ("pycopy", "pycopy", "const"),
        ("pycom", "pycom", "FAT"),
        ("ev3-pybricks", "pybricks.hubs", "EV3Brick"),
    ]:
        try:
            _t = __import__(mod_name, None, None, (mod_thing))
            info["family"] = fam_name
            del _t
            break
        except (ImportError, KeyError):
            pass

    if info["family"] == "ev3-pybricks":
        info["release"] = "2.0.0"

    if info["family"] == "micropython":
        info["version"]
        if (
            info["version"]
            and info["version"].endswith(".0")
            and info["version"] >= "1.10.0"  # versions from 1.10.0 to 1.23.2 do not have a micro .0
            and info["version"] <= "1.19.9"
        ):
            # versions from 1.10.0 to 1.23.2 do not have a micro .0
            info["version"] = info["version"][:-2]

    # spell-checker: disable
    if "mpy" in info and info["mpy"]:  # mpy on some v1.11+ builds
        sys_mpy = int(info["mpy"])
        # .mpy architecture
        arch = [
            None,
            "x86",
            "x64",
            "armv6",
            "armv6m",
            "armv7m",
            "armv7em",
            "armv7emsp",
            "armv7emdp",
            "xtensa",
            "xtensawin",
        ][sys_mpy >> 10]
        if arch:
            info["arch"] = arch
        # .mpy version.minor
        info["mpy"] = "v{}.{}".format(sys_mpy & 0xFF, sys_mpy >> 8 & 3)
    if info["build"] and not info["version"].endswith("-preview"):
        info["version"] = info["version"] + "-preview"
    # simple to use version[-build] string
    info["ver"] = f"{info['version']}-{info['build']}" if info["build"] else f"{info['version']}"

    return info


def version_str(version: tuple):  #  -> str:
    v_str = ".".join([str(n) for n in version[:3]])
    if len(version) > 3 and version[3]:
        v_str += "-" + version[3]
    return v_str


def get_boardname() -> str:
    "Read the board name from the boardname.py file that may have been created upfront"
    try:
        from boardname import BOARDNAME  # type: ignore

        log.info("Found BOARDNAME: {}".format(BOARDNAME))
    except ImportError:
        log.warning("BOARDNAME not found")
        BOARDNAME = ""
    return BOARDNAME


def get_root() -> str:  # sourcery skip: use-assigned-variable
    "Determine the root folder of the device"
    try:
        c = os.getcwd()
    except (OSError, AttributeError):
        # unix port
        c = "."
    r = c
    for r in [c, "/sd", "/flash", "/", "."]:
        try:
            _ = os.stat(r)
            break
        except OSError:
            continue
    return r


def file_exists(filename: str):
    try:
        if os.stat(filename)[0] >> 14:
            return True
        return False
    except OSError:
        return False


def show_help():
    print("-p, --path   path to store the stubs in, defaults to '.'")
    sys.exit(1)


def read_path() -> str:
    "get --path from cmdline. [unix/win]"
    path = ""
    if len(sys.argv) == 3:
        cmd = (sys.argv[1]).lower()
        if cmd in ("--path", "-p"):
            path = sys.argv[2]
        else:
            show_help()
    elif len(sys.argv) == 2:
        show_help()
    return path


def is_micropython() -> bool:
    "runtime test to determine full or micropython"
    # pylint: disable=unused-variable,eval-used
    try:
        # either test should fail on micropython

        # b) https://docs.micropython.org/en/latest/genrst/builtin_types.html#bytes-with-keywords-not-implemented
        # Micropython: NotImplementedError
        b = bytes("abc", encoding="utf8")  # type: ignore # lgtm [py/unused-local-variable]

        # c) https://docs.micropython.org/en/latest/genrst/core_language.html#function-objects-do-not-have-the-module-attribute
        # Micropython: AttributeError
        c = is_micropython.__module__  # type: ignore # lgtm [py/unused-local-variable]
        return False
    except (NotImplementedError, AttributeError):
        return True


SKIP_FILE = "modulelist.done"


def get_modules(skip=0):
    # new
    for p in LIBS:
        fname = p + "/modulelist.txt"
        if not file_exists(fname):
            continue
        try:
            with open(fname) as f:
                i = 0
                while True:
                    line = f.readline().strip()
                    if not line:
                        break
                    if len(line) > 0 and line[0] == "#":
                        continue
                    i += 1
                    if i < skip:
                        continue
                    yield line
                break
        except OSError:
            pass


def write_skip(done):
    # write count of modules already processed to file
    with open(SKIP_FILE, "w") as f:
        f.write(str(done) + "\n")


def read_skip():
    # read count of modules already processed from file
    done = 0
    try:
        with open(SKIP_FILE) as f:
            done = int(f.readline().strip())
    except OSError:
        pass
    return done


def main():
    import machine  # type: ignore

    was_running = file_exists(SKIP_FILE)
    if was_running:
        log.info("Continue from last run")
    else:
        log.info("Starting new run")
    # try:
    #     f = open("modulelist.done", "r+b")
    #     was_running = True
    #     print("Continue from last run")
    # except OSError:
    #     f = open("modulelist.done", "w+b")
    #     was_running = False
    stubber = Stubber(path=read_path())

    # f_name = "{}/{}".format(stubber.path, "modules.json")
    skip = 0
    if not was_running:
        # Only clean folder if this is a first run
        stubber.clean()
        stubber.report_start("modules.json")
    else:
        skip = read_skip()
        stubber._json_name = "{}/{}".format(stubber.path, "modules.json")

    for modulename in get_modules(skip):
        # ------------------------------------
        # do epic shit
        # but sometimes things fail / run out of memory and reboot
        try:
            stubber.create_one_stub(modulename)
        except MemoryError:
            # RESET AND HOPE THAT IN THE NEXT CYCLE WE PROGRESS FURTHER
            machine.reset()
        # -------------------------------------
        gc.collect()
        # modules_done[modulename] = str(stubber._report[-1] if ok else "failed")
        # with open("modulelist.done", "a") as f:
        #     f.write("{}={}\n".format(modulename, "ok" if ok else "failed"))
        skip += 1
        write_skip(skip)

    print("All modules have been processed, Finalizing report")
    stubber.report_end()


if __name__ == "__main__" or is_micropython():
    if not file_exists("no_auto_stubber.txt"):
        try:
            gc.threshold(4 * 1024)  # type: ignore
            gc.enable()
        except BaseException:
            pass
        main()
