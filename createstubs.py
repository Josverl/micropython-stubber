# create stubs for (all) modules on a micropython board
# ref: https://github.com/thonny/thonny/blob/786f63ff4460abe84f28c14dad2f9e78fe42cc49/thonny/plugins/micropython/__init__.py#L608

import gc
import logging
import uos as os

from machine import resetWDT
logging.basicConfig(level=logging.INFO)

class Stubber():
    def __init__(self, path="/flash/stubs"):
        # log = logging.getLogger(__name__)
        self._log = logging.getLogger('Stubber')
        self.path = path
        # self.path = "{}/{}/{}".format(path, os.uname()[0], os.uname()[2]).replace('.','_')
        #FIXME: create multilevel path
        # self._log.info('path {}'.format(self.path))
        # c = ""
        # for s in self.path.split('/'):
        #     self._log.info('s = {}'.format(s))
        #     if s != '':
        #         c += '/'+s
        #         try:
        #             self._log.info('mkdir {}'.format(c))
        #             os.mkdir(c)
        #         except:
        #             pass
        self._indent = 0
        self.problematic = ["upysh"]
            #"docs.conf", "pulseio.PWMOut", "adafruit_hid",
            # "webrepl", "gc", "http_client", "http_server",
        self.excluded = ["webrepl", "_webrepl"]

        #no option to discover modules from upythin, need to hardcode
        self.modules = [ ##Loboris
            '_thread', 'ak8963', 'array', 'binascii', 'btree', 'builtins',
            'cmath', 'collections', 'curl', 'display', 'errno', 'framebuf',
            'freesans20', 'functools', 'gc', 'gsm', 'hashlib', 'heapq', 'io',
            'json', 'logging', 'machine', 'math', 'microWebSocket', 'microWebSrv',
            'microWebTemplate', 'micropython', 'mpu6500', 'mpu9250', 'network', 'os',
            'pye', 'random', 're', 'requests', 'select', 'socket', 'ssd1306', 'ssh',
            'ssl', 'struct', 'sys', 'time', 'tpcalib', 'ubinascii', 'ucollections',
            'uctypes', 'uerrno', 'uhashlib', 'uheapq', 'uio', 'ujson', 'uos', 'upip',
            'upip_utarfile', 'upysh', 'urandom', 'ure', 'urequests', 'uselect', 'usocket',
            'ussl', 'ustruct', 'utime', 'utimeq', 'uzlib', 'websocket', 'writer', 'ymodem', 'zlib']

    def get_obj_attribs(self, obj: object):
        result = []
        errors = []
        #self._log.info('get attributes {} {}'.format(repr(obj),obj ))
        for name in dir(obj):
            try:
                val = getattr(obj, name)
                # name , value , type
                result.append((name, repr(val), repr(type(val)), val))
                #self._log.info( result[-1])
            except BaseException as e:
                errors.append("Couldn't get attribute '{}' from object '{}', Err: {}".format(name, obj, e))
        gc.collect()
        return result, errors

    def generate_all_stubs(self):
        try:
            for module_name in sorted(self.modules):
                if not module_name.startswith("_"):
                    file_name = "{}/{}.py".format(
                        self.path,
                        module_name.replace(".", "/")
                    )
                    self._log.info("dump module: {} to file: {}".format(module_name, file_name))
                    self.dump_module_stub(module_name, file_name)
        finally:
            self._log.info('Finally done')

    # Create a Stub of a single python module
    def dump_module_stub(self, module_name: str, file_name: str = None):
        if module_name.startswith("_") and module_name != '_thread':
            self._log.warning("SKIPPING internal module:{}".format(module_name))
            return
        if module_name in self.problematic:
            self._log.warning("SKIPPING problematic name:{}".format(module_name))
            return
        if file_name is None:
            file_name = module_name + ".py"

        #import the module (as new_module) to examine it
        try:
            new_module = __import__(module_name)
        except ImportError as e:
            #self._log.exception(e)
            self._log.error("Unable to import module: {}".format(module_name))
            return None, e
        except e:
            self._log.error("Failed to import Module: {}".format(module_name))
            #self._log.exception(e)
            return None, e

        #self._log.info( "create file : {} for {}".format(file_name,module_name))
        with open(file_name, "w") as fp:
            s = "\"Module '{}' on firmware '{}'\"\n".format(module_name, os.uname().version)
            fp.write(s)
            if module_name not in self.excluded:
                self._dump_object_stubs(fp, new_module, module_name, "")
            else:
                self._log.warning("skipped excluded module {}".format(module_name))

        if not module_name in ["sys", "logging", "gc"]:
            #try to unload the module
            try:
                #exec( "del sys.modules[\"{}\"]".format(module_name) )
                del new_module
            except BaseException:
                self._log.warning("could not unload module {}".format(module_name))
            finally:
                gc.collect()

    def _dump_object_stubs(self, fp, object_expr: object, obj_name: str, indent: str):
        from time import sleep_ms
        resetWDT() #avoid waking the dog 
        sleep_ms(2)
        if object_expr in self.problematic:
            self._log.warning("SKIPPING problematic name:" + object_expr)
            return

        self._log.debug("DUMPING : {}".format(object_expr))
        items, errors = self.get_obj_attribs(object_expr)
        if errors:
            self._log.error("ERRORS", errors)

        for name, rep, typ, obj in sorted(items, key=lambda x: x[0]):
            if name.startswith("__"):
                #skip internals
                continue

            # self._log.debug("DUMPING", indent, object_expr, name)
            self._log.debug("  * " + name + " : " + typ)

            if typ in ["<class 'function'>", "<class 'bound_method'>"]:
                s = indent + "def " + name + "():\n"
                s += indent + "    pass\n\n"
                fp.write(s)
                self._log.debug(s)

            elif typ in ["<class 'str'>", "<class 'int'>", "<class 'float'>"]:
                s = indent + name + " = " + rep + "\n"
                fp.write(s)
                self._log.debug(s)
            #new class
            elif typ == "<class 'type'>" and indent == "":
                # full expansion only on toplevel ?
                s = "\n{}class {}(): ...\n".format(indent, name)
                fp.write(s)
                self._log.debug(s)

                self._log.debug("#recursion !!")
                self._dump_object_stubs(fp, obj, "{0}.{1}".format(obj_name, name), indent + "    ")
            else:
                # keep only the name
                fp.write(indent + name + " = None\n")

    # def _get_builtins_info(self):
    #     # assume this runs on the host ?
    #     """
    #     for p in self.path:
    #         builtins_file = os.path.join(p, "__builtins__.py")
    #         if os.path.exists(builtins_file):
    #             return parse_api_information(builtins_file)
    #     """
    #     path = os.path.join(self.path, "builtins.py")
    #     if os.path.exists(path):
    #         return parse_api_information(path)
    #     else:
    #         return {}

try:
    #crude way to detect if the sd is already loaded
    _ = os.stat('/sd')
except OSError as e:
    _ = os.sdconfig(os.SDMODE_SPI, clk=18, mosi=23, miso=19, cs=4)
    _ = os.mountsd()


stubber = Stubber("/sd/stubs")
stubber.generate_all_stubs()


# for name in ['machine']:
#     stubber.dump_module_stub(name,'/flash/stubs/{}.py'.format(name))

# for name in modules:
#     print("Starting on module", name)
#     stubber.dump_module_stub(name,'/flash/stubs/{}.py'.format(name))
