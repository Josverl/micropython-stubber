# create stubs for (all) modules on a micropython board
# ref: https://github.com/thonny/thonny/blob/786f63ff4460abe84f28c14dad2f9e78fe42cc49/thonny/plugins/micropython/__init__.py#L608
import errno
import gc
import logging

import uos as os
from utime import sleep_us

# deal with firmware specific implementations
try:
    from machine import resetWDT
except:
    def resetWDT():
        pass

class Stubber():
    def __init__(self, path="/flash/stubs"):
        # log = logging.getLogger(__name__)
        self._log = logging.getLogger('Stubber')
        self._report = []
        u = os.uname()
        self._report.append( { 'sysname': u.sysname, 'nodename': u.nodename , 'release': u.release , 'version': u.version, 'machine': u.machine } )

        self.path = path
        try:
            self._log.info("stub path : {}".format(self.path))
            os.mkdir(self.path)
        except OSError as e:
            if e.args[0] != errno.EEXIST:
                self._log.exc(e, "error creating stub folder")
            #assume existing folder

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
        self.problematic = ["upysh", "webrepl_setup", "umqtt/simple", "umqtt/robust"]
        self.excluded = ["webrepl", "_webrepl", "webrepl_setup"]
        # FIXME: deal with umqtt/simple and /robust 
        # there is no option to discover modules from upython, need to hardcode
        # below contains the combines modules from ESP32 Micropython and Loboris Modules
        self.modules = ['_boot', '_onewire', '_thread', '_webrepl', 'ak8963', 'apa106', 'array', 'binascii', 'btree', 'builtins', 'cmath',
                        'collections', 'curl', 'dht', 'display', 'ds18x20', 'errno', 'esp', 'esp32', 'flashbdev', 'framebuf', 'freesans20',
                        'functools', 'gc', 'gsm', 'hashlib', 'heapq', 'inisetup', 'io', 'json', 'logging', 'machine', 'math', 'microWebSocket',
                        'microWebSrv', 'microWebTemplate', 'micropython', 'mpu6500', 'mpu9250', 'neopixel', 'network', 'ntptime', 'onewire', 'os', 'pyb',
                        'pye', 'random', 're', 'requests', 'select', 'socket', 'socketupip', 'ssd1306', 'ssh', 'ssl', 'struct', 'sys', 'time', 'tpcalib',
                        'ubinascii', 'ucollections', 'ucryptolib', 'uctypes', 'uerrno', 'uhashlib', 'uheapq', 'uio', 'ujson', 'umqtt/robust', 'umqtt/simple',
                        'uos', 'upip', 'upip_utarfile', 'upysh', 'urandom', 'ure', 'urequests', 'uselect', 'usocket', 'ussl', 'ustruct', 'utime', 'utimeq',
                        'uwebsocket', 'uzlib', 'webrepl', 'webrepl_setup', 'websocket', 'websocket_helper', 'writer', 'ymodem', 'zlib']

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
                    print("dump module: {} to file: {}".format(module_name, file_name))
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
            file_name = module_name.replace('.', '_') + ".py"
        #for nested modules
        module_name = module_name.replace('/', '.')

        #import the module (as new_module) to examine it
        try:
            new_module = __import__(module_name)
        except ImportError as e:
            #self._log.exception(e)
            self._log.warning("Unable to import module: {}".format(module_name))
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
                self._report.append({"module":module_name, "file": file_name})
            else:
                self._log.warning("skipped excluded module {}".format(module_name))

        if not module_name in ["os", "sys", "logging", "gc"]:
            #try to unload the module unless we use it
            try:
                del new_module
            except BaseException:
                self._log.warning("could not unload module {}".format(module_name))
            finally:
                gc.collect()

    def _dump_object_stubs(self, fp, object_expr: object, obj_name: str, indent: str):
        if object_expr in self.problematic:
            self._log.warning("SKIPPING problematic name:" + object_expr)
            return

        self._log.debug("DUMPING : {}".format(object_expr))
        items, errors = self.get_obj_attribs(object_expr)
        if errors:
            self._log.error(errors)

        for name, rep, typ, obj in sorted(items, key=lambda x: x[0]):
            if name.startswith("__"):
                #skip internals
                continue
            # allow the scheduler to run
            resetWDT()
            sleep_us(1)

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

    def clean(self):
        print("Clean/remove files in stubfolder")
        for fn in os.listdir(self.path):
            try:
                os.remove("{}/{}".format(self.path, fn))
            except:
                pass

    def report(self, filename="modules.json"):
        import ujson
        f_name = "{}/{}".format(self.path, filename)
        with open(f_name, 'w') as f:
            f.write(ujson.dumps(self._report))
        print("Created stubs for {} modules on board {} - {}".format(
            len(self._report)-1,
            os.uname().machine,
            os.uname().release))

def get_root():
    # Determine the root folder of the device
    try:
        r = "/flash"
        _ = os.stat(r)
    except OSError as e:
        if e.args[0] == errno.ENOENT:
            r = os.getcwd()
    finally:
        return r

#handle different file roots
path = "{}/stubs".format(get_root()).replace('//', '/')
try:
    os.mkdir(path)
except:
    pass
path = "{}/stubs/{}_{}".format(
    get_root(),
    os.uname().sysname,
    os.uname().release.replace('.', '_'),
    ).replace('//', '/')

logging.basicConfig(level=logging.INFO)

stubber = Stubber(path)
stubber.clean()
stubber.generate_all_stubs()

stubber.report()
