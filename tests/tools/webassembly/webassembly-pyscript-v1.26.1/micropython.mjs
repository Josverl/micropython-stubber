// This code implements the `-sMODULARIZE` settings by taking the generated
// JS program code (INNER_JS_CODE) and wrapping it in a factory function.

// When targetting node and ES6 we use `await import ..` in the generated code
// so the outer function needs to be marked as async.
async function _createMicroPythonModule(moduleArg = {}) {
  var moduleRtn;

// include: shell.js
// The Module object: Our interface to the outside world. We import
// and export values on it. There are various ways Module can be used:
// 1. Not defined. We create it here
// 2. A function parameter, function(moduleArg) => Promise<Module>
// 3. pre-run appended it, var Module = {}; ..generated code..
// 4. External script tag defines var Module.
// We need to check if Module already exists (e.g. case 3 above).
// Substitution will be replaced with actual code on later stage of the build,
// this way Closure Compiler will not mangle it (e.g. case 4. above).
// Note that if you want to run closure, and also to use Module
// after the generated code, you will need to define   var Module = {};
// before the code. Then that object will be used in the code, and you
// can continue to use Module afterwards as well.
var Module = moduleArg;

// Determine the runtime environment we are in. You can customize this by
// setting the ENVIRONMENT setting at compile time (see settings.js).

// Attempt to auto-detect the environment
var ENVIRONMENT_IS_WEB = typeof window == 'object';
var ENVIRONMENT_IS_WORKER = typeof WorkerGlobalScope != 'undefined';
// N.b. Electron.js environment is simultaneously a NODE-environment, but
// also a web environment.
var ENVIRONMENT_IS_NODE = typeof process == 'object' && process.versions?.node && process.type != 'renderer';
var ENVIRONMENT_IS_SHELL = !ENVIRONMENT_IS_WEB && !ENVIRONMENT_IS_NODE && !ENVIRONMENT_IS_WORKER;

if (ENVIRONMENT_IS_NODE) {
  // When building an ES module `require` is not normally available.
  // We need to use `createRequire()` to construct the require()` function.
  const { createRequire } = await import('module');
  /** @suppress{duplicate} */
  var require = createRequire(import.meta.url);

}

// --pre-jses are emitted after the Module integration code, so that they can
// refer to Module (if they choose; they can also define Module)


var arguments_ = [];
var thisProgram = './this.program';
var quit_ = (status, toThrow) => {
  throw toThrow;
};

var _scriptName = import.meta.url;

// `/` should be present at the end if `scriptDirectory` is not empty
var scriptDirectory = '';
function locateFile(path) {
  if (Module['locateFile']) {
    return Module['locateFile'](path, scriptDirectory);
  }
  return scriptDirectory + path;
}

// Hooks that are implemented differently in different runtime environments.
var readAsync, readBinary;

if (ENVIRONMENT_IS_NODE) {
  const isNode = typeof process == 'object' && process.versions?.node && process.type != 'renderer';
  if (!isNode) throw new Error('not compiled for this environment (did you build to HTML and try to run it not on the web, or set ENVIRONMENT to something - like node - and run it someplace else - like on the web?)');

  var nodeVersion = process.versions.node;
  var numericVersion = nodeVersion.split('.').slice(0, 3);
  numericVersion = (numericVersion[0] * 10000) + (numericVersion[1] * 100) + (numericVersion[2].split('-')[0] * 1);
  if (numericVersion < 160000) {
    throw new Error('This emscripten-generated code requires node v16.0.0 (detected v' + nodeVersion + ')');
  }

  // These modules will usually be used on Node.js. Load them eagerly to avoid
  // the complexity of lazy-loading.
  var fs = require('fs');

  if (_scriptName.startsWith('file:')) {
    scriptDirectory = require('path').dirname(require('url').fileURLToPath(_scriptName)) + '/';
  }

// include: node_shell_read.js
readBinary = (filename) => {
  // We need to re-wrap `file://` strings to URLs.
  filename = isFileURI(filename) ? new URL(filename) : filename;
  var ret = fs.readFileSync(filename);
  assert(Buffer.isBuffer(ret));
  return ret;
};

readAsync = async (filename, binary = true) => {
  // See the comment in the `readBinary` function.
  filename = isFileURI(filename) ? new URL(filename) : filename;
  var ret = fs.readFileSync(filename, binary ? undefined : 'utf8');
  assert(binary ? Buffer.isBuffer(ret) : typeof ret == 'string');
  return ret;
};
// end include: node_shell_read.js
  if (process.argv.length > 1) {
    thisProgram = process.argv[1].replace(/\\/g, '/');
  }

  arguments_ = process.argv.slice(2);

  quit_ = (status, toThrow) => {
    process.exitCode = status;
    throw toThrow;
  };

} else
if (ENVIRONMENT_IS_SHELL) {

  const isNode = typeof process == 'object' && process.versions?.node && process.type != 'renderer';
  if (isNode || typeof window == 'object' || typeof WorkerGlobalScope != 'undefined') throw new Error('not compiled for this environment (did you build to HTML and try to run it not on the web, or set ENVIRONMENT to something - like node - and run it someplace else - like on the web?)');

} else

// Note that this includes Node.js workers when relevant (pthreads is enabled).
// Node.js workers are detected as a combination of ENVIRONMENT_IS_WORKER and
// ENVIRONMENT_IS_NODE.
if (ENVIRONMENT_IS_WEB || ENVIRONMENT_IS_WORKER) {
  try {
    scriptDirectory = new URL('.', _scriptName).href; // includes trailing slash
  } catch {
    // Must be a `blob:` or `data:` URL (e.g. `blob:http://site.com/etc/etc`), we cannot
    // infer anything from them.
  }

  if (!(typeof window == 'object' || typeof WorkerGlobalScope != 'undefined')) throw new Error('not compiled for this environment (did you build to HTML and try to run it not on the web, or set ENVIRONMENT to something - like node - and run it someplace else - like on the web?)');

  {
// include: web_or_worker_shell_read.js
if (ENVIRONMENT_IS_WORKER) {
    readBinary = (url) => {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', url, false);
      xhr.responseType = 'arraybuffer';
      xhr.send(null);
      return new Uint8Array(/** @type{!ArrayBuffer} */(xhr.response));
    };
  }

  readAsync = async (url) => {
    // Fetch has some additional restrictions over XHR, like it can't be used on a file:// url.
    // See https://github.com/github/fetch/pull/92#issuecomment-140665932
    // Cordova or Electron apps are typically loaded from a file:// url.
    // So use XHR on webview if URL is a file URL.
    if (isFileURI(url)) {
      return new Promise((resolve, reject) => {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.responseType = 'arraybuffer';
        xhr.onload = () => {
          if (xhr.status == 200 || (xhr.status == 0 && xhr.response)) { // file URLs can return 0
            resolve(xhr.response);
            return;
          }
          reject(xhr.status);
        };
        xhr.onerror = reject;
        xhr.send(null);
      });
    }
    var response = await fetch(url, { credentials: 'same-origin' });
    if (response.ok) {
      return response.arrayBuffer();
    }
    throw new Error(response.status + ' : ' + response.url);
  };
// end include: web_or_worker_shell_read.js
  }
} else
{
  throw new Error('environment detection error');
}

var out = console.log.bind(console);
var err = console.error.bind(console);

var IDBFS = 'IDBFS is no longer included by default; build with -lidbfs.js';
var PROXYFS = 'PROXYFS is no longer included by default; build with -lproxyfs.js';
var WORKERFS = 'WORKERFS is no longer included by default; build with -lworkerfs.js';
var FETCHFS = 'FETCHFS is no longer included by default; build with -lfetchfs.js';
var ICASEFS = 'ICASEFS is no longer included by default; build with -licasefs.js';
var JSFILEFS = 'JSFILEFS is no longer included by default; build with -ljsfilefs.js';
var OPFS = 'OPFS is no longer included by default; build with -lopfs.js';

var NODEFS = 'NODEFS is no longer included by default; build with -lnodefs.js';

// perform assertions in shell.js after we set up out() and err(), as otherwise
// if an assertion fails it cannot print the message

assert(!ENVIRONMENT_IS_SHELL, 'shell environment detected but not enabled at build time.  Add `shell` to `-sENVIRONMENT` to enable.');

// end include: shell.js

// include: preamble.js
// === Preamble library stuff ===

// Documentation for the public APIs defined in this file must be updated in:
//    site/source/docs/api_reference/preamble.js.rst
// A prebuilt local version of the documentation is available at:
//    site/build/text/docs/api_reference/preamble.js.txt
// You can also build docs locally as HTML or other formats in site/
// An online HTML version (which may be of a different version of Emscripten)
//    is up at http://kripken.github.io/emscripten-site/docs/api_reference/preamble.js.html

var wasmBinary;

if (typeof WebAssembly != 'object') {
  err('no native wasm support detected');
}

// Wasm globals

//========================================
// Runtime essentials
//========================================

// whether we are quitting the application. no code should run after this.
// set in exit() and abort()
var ABORT = false;

// set by exit() and abort().  Passed to 'onExit' handler.
// NOTE: This is also used as the process return code code in shell environments
// but only when noExitRuntime is false.
var EXITSTATUS;

// In STRICT mode, we only define assert() when ASSERTIONS is set.  i.e. we
// don't define it at all in release modes.  This matches the behaviour of
// MINIMAL_RUNTIME.
// TODO(sbc): Make this the default even without STRICT enabled.
/** @type {function(*, string=)} */
function assert(condition, text) {
  if (!condition) {
    abort('Assertion failed' + (text ? ': ' + text : ''));
  }
}

// We used to include malloc/free by default in the past. Show a helpful error in
// builds with assertions.
function _malloc() {
  abort('malloc() called but not included in the build - add `_malloc` to EXPORTED_FUNCTIONS');
}
function _free() {
  // Show a helpful error since we used to include free by default in the past.
  abort('free() called but not included in the build - add `_free` to EXPORTED_FUNCTIONS');
}

/**
 * Indicates whether filename is delivered via file protocol (as opposed to http/https)
 * @noinline
 */
var isFileURI = (filename) => filename.startsWith('file://');

// include: runtime_common.js
// include: runtime_stack_check.js
// Initializes the stack cookie. Called at the startup of main and at the startup of each thread in pthreads mode.
function writeStackCookie() {
  var max = _emscripten_stack_get_end();
  assert((max & 3) == 0);
  // If the stack ends at address zero we write our cookies 4 bytes into the
  // stack.  This prevents interference with SAFE_HEAP and ASAN which also
  // monitor writes to address zero.
  if (max == 0) {
    max += 4;
  }
  // The stack grow downwards towards _emscripten_stack_get_end.
  // We write cookies to the final two words in the stack and detect if they are
  // ever overwritten.
  HEAPU32[((max)>>2)] = 0x02135467;
  HEAPU32[(((max)+(4))>>2)] = 0x89BACDFE;
  // Also test the global address 0 for integrity.
  HEAPU32[((0)>>2)] = 1668509029;
}

function checkStackCookie() {
  if (ABORT) return;
  var max = _emscripten_stack_get_end();
  // See writeStackCookie().
  if (max == 0) {
    max += 4;
  }
  var cookie1 = HEAPU32[((max)>>2)];
  var cookie2 = HEAPU32[(((max)+(4))>>2)];
  if (cookie1 != 0x02135467 || cookie2 != 0x89BACDFE) {
    abort(`Stack overflow! Stack cookie has been overwritten at ${ptrToString(max)}, expected hex dwords 0x89BACDFE and 0x2135467, but received ${ptrToString(cookie2)} ${ptrToString(cookie1)}`);
  }
  // Also test the global address 0 for integrity.
  if (HEAPU32[((0)>>2)] != 0x63736d65 /* 'emsc' */) {
    abort('Runtime error: The application has corrupted its heap memory area (address zero)!');
  }
}
// end include: runtime_stack_check.js
// include: runtime_exceptions.js
// end include: runtime_exceptions.js
// include: runtime_debug.js
var runtimeDebug = true; // Switch to false at runtime to disable logging at the right times

// Used by XXXXX_DEBUG settings to output debug messages.
function dbg(...args) {
  if (!runtimeDebug && typeof runtimeDebug != 'undefined') return;
  // TODO(sbc): Make this configurable somehow.  Its not always convenient for
  // logging to show up as warnings.
  console.warn(...args);
}

// Endianness check
(() => {
  var h16 = new Int16Array(1);
  var h8 = new Int8Array(h16.buffer);
  h16[0] = 0x6373;
  if (h8[0] !== 0x73 || h8[1] !== 0x63) abort('Runtime error: expected the system to be little-endian! (Run with -sSUPPORT_BIG_ENDIAN to bypass)');
})();

function consumedModuleProp(prop) {
  if (!Object.getOwnPropertyDescriptor(Module, prop)) {
    Object.defineProperty(Module, prop, {
      configurable: true,
      set() {
        abort(`Attempt to set \`Module.${prop}\` after it has already been processed.  This can happen, for example, when code is injected via '--post-js' rather than '--pre-js'`);

      }
    });
  }
}

function makeInvalidEarlyAccess(name) {
  return () => assert(false, `call to '${name}' via reference taken before Wasm module initialization`);

}

function ignoredModuleProp(prop) {
  if (Object.getOwnPropertyDescriptor(Module, prop)) {
    abort(`\`Module.${prop}\` was supplied but \`${prop}\` not included in INCOMING_MODULE_JS_API`);
  }
}

// forcing the filesystem exports a few things by default
function isExportedByForceFilesystem(name) {
  return name === 'FS_createPath' ||
         name === 'FS_createDataFile' ||
         name === 'FS_createPreloadedFile' ||
         name === 'FS_preloadFile' ||
         name === 'FS_unlink' ||
         name === 'addRunDependency' ||
         // The old FS has some functionality that WasmFS lacks.
         name === 'FS_createLazyFile' ||
         name === 'FS_createDevice' ||
         name === 'removeRunDependency';
}

function missingLibrarySymbol(sym) {

  // Any symbol that is not included from the JS library is also (by definition)
  // not exported on the Module object.
  unexportedRuntimeSymbol(sym);
}

function unexportedRuntimeSymbol(sym) {
  if (!Object.getOwnPropertyDescriptor(Module, sym)) {
    Object.defineProperty(Module, sym, {
      configurable: true,
      get() {
        var msg = `'${sym}' was not exported. add it to EXPORTED_RUNTIME_METHODS (see the Emscripten FAQ)`;
        if (isExportedByForceFilesystem(sym)) {
          msg += '. Alternatively, forcing filesystem support (-sFORCE_FILESYSTEM) can export this for you';
        }
        abort(msg);
      }
    });
  }
}

// end include: runtime_debug.js
var readyPromiseResolve, readyPromiseReject;

// Memory management

var wasmMemory;

var
/** @type {!Int8Array} */
  HEAP8,
/** @type {!Uint8Array} */
  HEAPU8,
/** @type {!Int16Array} */
  HEAP16,
/** @type {!Uint16Array} */
  HEAPU16,
/** @type {!Int32Array} */
  HEAP32,
/** @type {!Uint32Array} */
  HEAPU32,
/** @type {!Float32Array} */
  HEAPF32,
/** @type {!Float64Array} */
  HEAPF64;

// BigInt64Array type is not correctly defined in closure
var
/** not-@type {!BigInt64Array} */
  HEAP64,
/* BigUint64Array type is not correctly defined in closure
/** not-@type {!BigUint64Array} */
  HEAPU64;

var runtimeInitialized = false;



function updateMemoryViews() {
  var b = wasmMemory.buffer;
  HEAP8 = new Int8Array(b);
  HEAP16 = new Int16Array(b);
  HEAPU8 = new Uint8Array(b);
  HEAPU16 = new Uint16Array(b);
  HEAP32 = new Int32Array(b);
  HEAPU32 = new Uint32Array(b);
  HEAPF32 = new Float32Array(b);
  HEAPF64 = new Float64Array(b);
  HEAP64 = new BigInt64Array(b);
  HEAPU64 = new BigUint64Array(b);
}

// include: memoryprofiler.js
// end include: memoryprofiler.js
// end include: runtime_common.js
assert(typeof Int32Array != 'undefined' && typeof Float64Array !== 'undefined' && Int32Array.prototype.subarray != undefined && Int32Array.prototype.set != undefined,
       'JS engine does not provide full typed array support');

function preRun() {
  if (Module['preRun']) {
    if (typeof Module['preRun'] == 'function') Module['preRun'] = [Module['preRun']];
    while (Module['preRun'].length) {
      addOnPreRun(Module['preRun'].shift());
    }
  }
  consumedModuleProp('preRun');
  // Begin ATPRERUNS hooks
  callRuntimeCallbacks(onPreRuns);
  // End ATPRERUNS hooks
}

function initRuntime() {
  assert(!runtimeInitialized);
  runtimeInitialized = true;

  checkStackCookie();

  // No ATINITS hooks

  wasmExports['__wasm_call_ctors']();

  // No ATPOSTCTORS hooks
}

function postRun() {
  checkStackCookie();
   // PThreads reuse the runtime from the main thread.

  if (Module['postRun']) {
    if (typeof Module['postRun'] == 'function') Module['postRun'] = [Module['postRun']];
    while (Module['postRun'].length) {
      addOnPostRun(Module['postRun'].shift());
    }
  }
  consumedModuleProp('postRun');

  // Begin ATPOSTRUNS hooks
  callRuntimeCallbacks(onPostRuns);
  // End ATPOSTRUNS hooks
}

/** @param {string|number=} what */
function abort(what) {
  Module['onAbort']?.(what);

  what = 'Aborted(' + what + ')';
  // TODO(sbc): Should we remove printing and leave it up to whoever
  // catches the exception?
  err(what);

  ABORT = true;

  // Use a wasm runtime error, because a JS error might be seen as a foreign
  // exception, which means we'd run destructors on it. We need the error to
  // simply make the program stop.
  // FIXME This approach does not work in Wasm EH because it currently does not assume
  // all RuntimeErrors are from traps; it decides whether a RuntimeError is from
  // a trap or not based on a hidden field within the object. So at the moment
  // we don't have a way of throwing a wasm trap from JS. TODO Make a JS API that
  // allows this in the wasm spec.

  // Suppress closure compiler warning here. Closure compiler's builtin extern
  // definition for WebAssembly.RuntimeError claims it takes no arguments even
  // though it can.
  // TODO(https://github.com/google/closure-compiler/pull/3913): Remove if/when upstream closure gets fixed.
  /** @suppress {checkTypes} */
  var e = new WebAssembly.RuntimeError(what);

  readyPromiseReject?.(e);
  // Throw the error whether or not MODULARIZE is set because abort is used
  // in code paths apart from instantiation where an exception is expected
  // to be thrown when abort is called.
  throw e;
}

// show errors on likely calls to FS when it was not included
var FS = {
  error() {
    abort('Filesystem support (FS) was not included. The problem is that you are using files from JS, but files were not used from C/C++, so filesystem support was not auto-included. You can force-include filesystem support with -sFORCE_FILESYSTEM');
  },
  init() { FS.error() },
  createDataFile() { FS.error() },
  createPreloadedFile() { FS.error() },
  createLazyFile() { FS.error() },
  open() { FS.error() },
  mkdev() { FS.error() },
  registerDevice() { FS.error() },
  analyzePath() { FS.error() },

  ErrnoError() { FS.error() },
};


function createExportWrapper(name, nargs) {
  return (...args) => {
    assert(runtimeInitialized, `native function \`${name}\` called before runtime initialization`);
    var f = wasmExports[name];
    assert(f, `exported native function \`${name}\` not found`);
    // Only assert for too many arguments. Too few can be valid since the missing arguments will be zero filled.
    assert(args.length <= nargs, `native function \`${name}\` called with ${args.length} args but expects ${nargs}`);
    return f(...args);
  };
}

var wasmBinaryFile;

function findWasmBinary() {
  if (Module['locateFile']) {
    return locateFile('micropython.wasm');
  }
  // Use bundler-friendly `new URL(..., import.meta.url)` pattern; works in browsers too.
  return new URL('micropython.wasm', import.meta.url).href;
}

function getBinarySync(file) {
  if (file == wasmBinaryFile && wasmBinary) {
    return new Uint8Array(wasmBinary);
  }
  if (readBinary) {
    return readBinary(file);
  }
  // Throwing a plain string here, even though it not normally adviables since
  // this gets turning into an `abort` in instantiateArrayBuffer.
  throw 'both async and sync fetching of the wasm failed';
}

async function getWasmBinary(binaryFile) {
  // If we don't have the binary yet, load it asynchronously using readAsync.
  if (!wasmBinary) {
    // Fetch the binary using readAsync
    try {
      var response = await readAsync(binaryFile);
      return new Uint8Array(response);
    } catch {
      // Fall back to getBinarySync below;
    }
  }

  // Otherwise, getBinarySync should be able to get it synchronously
  return getBinarySync(binaryFile);
}

async function instantiateArrayBuffer(binaryFile, imports) {
  try {
    var binary = await getWasmBinary(binaryFile);
    var instance = await WebAssembly.instantiate(binary, imports);
    return instance;
  } catch (reason) {
    err(`failed to asynchronously prepare wasm: ${reason}`);

    // Warn on some common problems.
    if (isFileURI(binaryFile)) {
      err(`warning: Loading from a file URI (${binaryFile}) is not supported in most browsers. See https://emscripten.org/docs/getting_started/FAQ.html#how-do-i-run-a-local-webserver-for-testing-why-does-my-program-stall-in-downloading-or-preparing`);
    }
    abort(reason);
  }
}

async function instantiateAsync(binary, binaryFile, imports) {
  if (!binary
      // Don't use streaming for file:// delivered objects in a webview, fetch them synchronously.
      && !isFileURI(binaryFile)
      // Avoid instantiateStreaming() on Node.js environment for now, as while
      // Node.js v18.1.0 implements it, it does not have a full fetch()
      // implementation yet.
      //
      // Reference:
      //   https://github.com/emscripten-core/emscripten/pull/16917
      && !ENVIRONMENT_IS_NODE
     ) {
    try {
      var response = fetch(binaryFile, { credentials: 'same-origin' });
      var instantiationResult = await WebAssembly.instantiateStreaming(response, imports);
      return instantiationResult;
    } catch (reason) {
      // We expect the most common failure cause to be a bad MIME type for the binary,
      // in which case falling back to ArrayBuffer instantiation should work.
      err(`wasm streaming compile failed: ${reason}`);
      err('falling back to ArrayBuffer instantiation');
      // fall back of instantiateArrayBuffer below
    };
  }
  return instantiateArrayBuffer(binaryFile, imports);
}

function getWasmImports() {
  // prepare imports
  return {
    'env': wasmImports,
    'wasi_snapshot_preview1': wasmImports,
  }
}

// Create the wasm instance.
// Receives the wasm imports, returns the exports.
async function createWasm() {
  // Load the wasm module and create an instance of using native support in the JS engine.
  // handle a generated wasm instance, receiving its exports and
  // performing other necessary setup
  /** @param {WebAssembly.Module=} module*/
  function receiveInstance(instance, module) {
    wasmExports = instance.exports;

    

    wasmMemory = wasmExports['memory'];
    
    assert(wasmMemory, 'memory not found in wasm exports');
    updateMemoryViews();

    assignWasmExports(wasmExports);
    return wasmExports;
  }

  // Prefer streaming instantiation if available.
  // Async compilation can be confusing when an error on the page overwrites Module
  // (for example, if the order of elements is wrong, and the one defining Module is
  // later), so we save Module and check it later.
  var trueModule = Module;
  function receiveInstantiationResult(result) {
    // 'result' is a ResultObject object which has both the module and instance.
    // receiveInstance() will swap in the exports (to Module.asm) so they can be called
    assert(Module === trueModule, 'the Module object should not be replaced during async compilation - perhaps the order of HTML elements is wrong?');
    trueModule = null;
    // TODO: Due to Closure regression https://github.com/google/closure-compiler/issues/3193, the above line no longer optimizes out down to the following line.
    // When the regression is fixed, can restore the above PTHREADS-enabled path.
    return receiveInstance(result['instance']);
  }

  var info = getWasmImports();

  // User shell pages can write their own Module.instantiateWasm = function(imports, successCallback) callback
  // to manually instantiate the Wasm module themselves. This allows pages to
  // run the instantiation parallel to any other async startup actions they are
  // performing.
  // Also pthreads and wasm workers initialize the wasm instance through this
  // path.
  if (Module['instantiateWasm']) {
    return new Promise((resolve, reject) => {
      try {
        Module['instantiateWasm'](info, (mod, inst) => {
          resolve(receiveInstance(mod, inst));
        });
      } catch(e) {
        err(`Module.instantiateWasm callback failed with error: ${e}`);
        reject(e);
      }
    });
  }

  wasmBinaryFile ??= findWasmBinary();
  var result = await instantiateAsync(wasmBinary, wasmBinaryFile, info);
  var exports = receiveInstantiationResult(result);
  return exports;
}

// end include: preamble.js

// Begin JS library code


  class ExitStatus {
      name = 'ExitStatus';
      constructor(status) {
        this.message = `Program terminated with exit(${status})`;
        this.status = status;
      }
    }

  var callRuntimeCallbacks = (callbacks) => {
      while (callbacks.length > 0) {
        // Pass the module as the first argument.
        callbacks.shift()(Module);
      }
    };
  var onPostRuns = [];
  var addOnPostRun = (cb) => onPostRuns.push(cb);

  var onPreRuns = [];
  var addOnPreRun = (cb) => onPreRuns.push(cb);


  
    /**
     * @param {number} ptr
     * @param {string} type
     */
  function getValue(ptr, type = 'i8') {
    if (type.endsWith('*')) type = '*';
    switch (type) {
      case 'i1': return HEAP8[ptr];
      case 'i8': return HEAP8[ptr];
      case 'i16': return HEAP16[((ptr)>>1)];
      case 'i32': return HEAP32[((ptr)>>2)];
      case 'i64': return HEAP64[((ptr)>>3)];
      case 'float': return HEAPF32[((ptr)>>2)];
      case 'double': return HEAPF64[((ptr)>>3)];
      case '*': return HEAPU32[((ptr)>>2)];
      default: abort(`invalid type for getValue: ${type}`);
    }
  }

  var noExitRuntime = true;

  var ptrToString = (ptr) => {
      assert(typeof ptr === 'number');
      // Convert to 32-bit unsigned value
      ptr >>>= 0;
      return '0x' + ptr.toString(16).padStart(8, '0');
    };

  
    /**
     * @param {number} ptr
     * @param {number} value
     * @param {string} type
     */
  function setValue(ptr, value, type = 'i8') {
    if (type.endsWith('*')) type = '*';
    switch (type) {
      case 'i1': HEAP8[ptr] = value; break;
      case 'i8': HEAP8[ptr] = value; break;
      case 'i16': HEAP16[((ptr)>>1)] = value; break;
      case 'i32': HEAP32[((ptr)>>2)] = value; break;
      case 'i64': HEAP64[((ptr)>>3)] = BigInt(value); break;
      case 'float': HEAPF32[((ptr)>>2)] = value; break;
      case 'double': HEAPF64[((ptr)>>3)] = value; break;
      case '*': HEAPU32[((ptr)>>2)] = value; break;
      default: abort(`invalid type for setValue: ${type}`);
    }
  }

  var stackRestore = (val) => __emscripten_stack_restore(val);

  var stackSave = () => _emscripten_stack_get_current();

  var warnOnce = (text) => {
      warnOnce.shown ||= {};
      if (!warnOnce.shown[text]) {
        warnOnce.shown[text] = 1;
        if (ENVIRONMENT_IS_NODE) text = 'warning: ' + text;
        err(text);
      }
    };

  var UTF8Decoder = typeof TextDecoder != 'undefined' ? new TextDecoder() : undefined;
  
  var findStringEnd = (heapOrArray, idx, maxBytesToRead, ignoreNul) => {
      var maxIdx = idx + maxBytesToRead;
      if (ignoreNul) return maxIdx;
      // TextDecoder needs to know the byte length in advance, it doesn't stop on
      // null terminator by itself.
      // As a tiny code save trick, compare idx against maxIdx using a negation,
      // so that maxBytesToRead=undefined/NaN means Infinity.
      while (heapOrArray[idx] && !(idx >= maxIdx)) ++idx;
      return idx;
    };
  
  
    /**
     * Given a pointer 'idx' to a null-terminated UTF8-encoded string in the given
     * array that contains uint8 values, returns a copy of that string as a
     * Javascript String object.
     * heapOrArray is either a regular array, or a JavaScript typed array view.
     * @param {number=} idx
     * @param {number=} maxBytesToRead
     * @param {boolean=} ignoreNul - If true, the function will not stop on a NUL character.
     * @return {string}
     */
  var UTF8ArrayToString = (heapOrArray, idx = 0, maxBytesToRead, ignoreNul) => {
  
      var endPtr = findStringEnd(heapOrArray, idx, maxBytesToRead, ignoreNul);
  
      // When using conditional TextDecoder, skip it for short strings as the overhead of the native call is not worth it.
      if (endPtr - idx > 16 && heapOrArray.buffer && UTF8Decoder) {
        return UTF8Decoder.decode(heapOrArray.subarray(idx, endPtr));
      }
      var str = '';
      while (idx < endPtr) {
        // For UTF8 byte structure, see:
        // http://en.wikipedia.org/wiki/UTF-8#Description
        // https://www.ietf.org/rfc/rfc2279.txt
        // https://tools.ietf.org/html/rfc3629
        var u0 = heapOrArray[idx++];
        if (!(u0 & 0x80)) { str += String.fromCharCode(u0); continue; }
        var u1 = heapOrArray[idx++] & 63;
        if ((u0 & 0xE0) == 0xC0) { str += String.fromCharCode(((u0 & 31) << 6) | u1); continue; }
        var u2 = heapOrArray[idx++] & 63;
        if ((u0 & 0xF0) == 0xE0) {
          u0 = ((u0 & 15) << 12) | (u1 << 6) | u2;
        } else {
          if ((u0 & 0xF8) != 0xF0) warnOnce('Invalid UTF-8 leading byte ' + ptrToString(u0) + ' encountered when deserializing a UTF-8 string in wasm memory to a JS string!');
          u0 = ((u0 & 7) << 18) | (u1 << 12) | (u2 << 6) | (heapOrArray[idx++] & 63);
        }
  
        if (u0 < 0x10000) {
          str += String.fromCharCode(u0);
        } else {
          var ch = u0 - 0x10000;
          str += String.fromCharCode(0xD800 | (ch >> 10), 0xDC00 | (ch & 0x3FF));
        }
      }
      return str;
    };
  
    /**
     * Given a pointer 'ptr' to a null-terminated UTF8-encoded string in the
     * emscripten HEAP, returns a copy of that string as a Javascript String object.
     *
     * @param {number} ptr
     * @param {number=} maxBytesToRead - An optional length that specifies the
     *   maximum number of bytes to read. You can omit this parameter to scan the
     *   string until the first 0 byte. If maxBytesToRead is passed, and the string
     *   at [ptr, ptr+maxBytesToReadr[ contains a null byte in the middle, then the
     *   string will cut short at that byte index.
     * @param {boolean=} ignoreNul - If true, the function will not stop on a NUL character.
     * @return {string}
     */
  var UTF8ToString = (ptr, maxBytesToRead, ignoreNul) => {
      assert(typeof ptr == 'number', `UTF8ToString expects a number (got ${typeof ptr})`);
      return ptr ? UTF8ArrayToString(HEAPU8, ptr, maxBytesToRead, ignoreNul) : '';
    };
  var SYSCALLS = {
  varargs:undefined,
  getStr(ptr) {
        var ret = UTF8ToString(ptr);
        return ret;
      },
  };
  var _fd_close = (fd) => {
      abort('fd_close called without SYSCALLS_REQUIRE_FILESYSTEM');
    };

  var INT53_MAX = 9007199254740992;
  
  var INT53_MIN = -9007199254740992;
  var bigintToI53Checked = (num) => (num < INT53_MIN || num > INT53_MAX) ? NaN : Number(num);
  function _fd_seek(fd, offset, whence, newOffset) {
    offset = bigintToI53Checked(offset);
  
  
      return 70;
    ;
  }

  var printCharBuffers = [null,[],[]];
  
  var printChar = (stream, curr) => {
      var buffer = printCharBuffers[stream];
      assert(buffer);
      if (curr === 0 || curr === 10) {
        (stream === 1 ? out : err)(UTF8ArrayToString(buffer));
        buffer.length = 0;
      } else {
        buffer.push(curr);
      }
    };
  
  var flush_NO_FILESYSTEM = () => {
      // flush anything remaining in the buffers during shutdown
      _fflush(0);
      if (printCharBuffers[1].length) printChar(1, 10);
      if (printCharBuffers[2].length) printChar(2, 10);
    };
  
  
  var _fd_write = (fd, iov, iovcnt, pnum) => {
      // hack to support printf in SYSCALLS_REQUIRE_FILESYSTEM=0
      var num = 0;
      for (var i = 0; i < iovcnt; i++) {
        var ptr = HEAPU32[((iov)>>2)];
        var len = HEAPU32[(((iov)+(4))>>2)];
        iov += 8;
        for (var j = 0; j < len; j++) {
          printChar(fd, HEAPU8[ptr+j]);
        }
        num += len;
      }
      HEAPU32[((pnum)>>2)] = num;
      return 0;
    };
// End JS library code

// include: postlibrary.js
// This file is included after the automatically-generated JS library code
// but before the wasm module is created.

{

  // Begin ATMODULES hooks
  if (Module['noExitRuntime']) noExitRuntime = Module['noExitRuntime'];
if (Module['print']) out = Module['print'];
if (Module['printErr']) err = Module['printErr'];
if (Module['wasmBinary']) wasmBinary = Module['wasmBinary'];

Module['FS_createDataFile'] = FS.createDataFile;
Module['FS_createPreloadedFile'] = FS.createPreloadedFile;

  // End ATMODULES hooks

  checkIncomingModuleAPI();

  if (Module['arguments']) arguments_ = Module['arguments'];
  if (Module['thisProgram']) thisProgram = Module['thisProgram'];

  // Assertions on removed incoming Module JS APIs.
  assert(typeof Module['memoryInitializerPrefixURL'] == 'undefined', 'Module.memoryInitializerPrefixURL option was removed, use Module.locateFile instead');
  assert(typeof Module['pthreadMainPrefixURL'] == 'undefined', 'Module.pthreadMainPrefixURL option was removed, use Module.locateFile instead');
  assert(typeof Module['cdInitializerPrefixURL'] == 'undefined', 'Module.cdInitializerPrefixURL option was removed, use Module.locateFile instead');
  assert(typeof Module['filePackagePrefixURL'] == 'undefined', 'Module.filePackagePrefixURL option was removed, use Module.locateFile instead');
  assert(typeof Module['read'] == 'undefined', 'Module.read option was removed');
  assert(typeof Module['readAsync'] == 'undefined', 'Module.readAsync option was removed (modify readAsync in JS)');
  assert(typeof Module['readBinary'] == 'undefined', 'Module.readBinary option was removed (modify readBinary in JS)');
  assert(typeof Module['setWindowTitle'] == 'undefined', 'Module.setWindowTitle option was removed (modify emscripten_set_window_title in JS)');
  assert(typeof Module['TOTAL_MEMORY'] == 'undefined', 'Module.TOTAL_MEMORY has been renamed Module.INITIAL_MEMORY');
  assert(typeof Module['ENVIRONMENT'] == 'undefined', 'Module.ENVIRONMENT has been deprecated. To force the environment, use the ENVIRONMENT compile-time option (for example, -sENVIRONMENT=web or -sENVIRONMENT=node)');
  assert(typeof Module['STACK_SIZE'] == 'undefined', 'STACK_SIZE can no longer be set at runtime.  Use -sSTACK_SIZE at link time')
  // If memory is defined in wasm, the user can't provide it, or set INITIAL_MEMORY
  assert(typeof Module['wasmMemory'] == 'undefined', 'Use of `wasmMemory` detected.  Use -sIMPORTED_MEMORY to define wasmMemory externally');
  assert(typeof Module['INITIAL_MEMORY'] == 'undefined', 'Detected runtime INITIAL_MEMORY setting.  Use -sIMPORTED_MEMORY to define wasmMemory dynamically');

  if (Module['preInit']) {
    if (typeof Module['preInit'] == 'function') Module['preInit'] = [Module['preInit']];
    while (Module['preInit'].length > 0) {
      Module['preInit'].shift()();
    }
  }
  consumedModuleProp('preInit');
}

// Begin runtime exports
  var missingLibrarySymbols = [
  'writeI53ToI64',
  'writeI53ToI64Clamped',
  'writeI53ToI64Signaling',
  'writeI53ToU64Clamped',
  'writeI53ToU64Signaling',
  'readI53FromI64',
  'readI53FromU64',
  'convertI32PairToI53',
  'convertI32PairToI53Checked',
  'convertU32PairToI53',
  'stackAlloc',
  'getTempRet0',
  'setTempRet0',
  'zeroMemory',
  'exitJS',
  'getHeapMax',
  'abortOnCannotGrowMemory',
  'growMemory',
  'withStackSave',
  'strError',
  'inetPton4',
  'inetNtop4',
  'inetPton6',
  'inetNtop6',
  'readSockaddr',
  'writeSockaddr',
  'readEmAsmArgs',
  'jstoi_q',
  'getExecutableName',
  'autoResumeAudioContext',
  'getDynCaller',
  'dynCall',
  'handleException',
  'keepRuntimeAlive',
  'runtimeKeepalivePush',
  'runtimeKeepalivePop',
  'callUserCallback',
  'maybeExit',
  'asyncLoad',
  'asmjsMangle',
  'alignMemory',
  'mmapAlloc',
  'HandleAllocator',
  'getNativeTypeSize',
  'getUniqueRunDependency',
  'addRunDependency',
  'removeRunDependency',
  'addOnInit',
  'addOnPostCtor',
  'addOnPreMain',
  'addOnExit',
  'STACK_SIZE',
  'STACK_ALIGN',
  'POINTER_SIZE',
  'ASSERTIONS',
  'ccall',
  'cwrap',
  'convertJsFunctionToWasm',
  'getEmptyTableSlot',
  'updateTableMap',
  'getFunctionAddress',
  'addFunction',
  'removeFunction',
  'stringToUTF8Array',
  'stringToUTF8',
  'lengthBytesUTF8',
  'intArrayFromString',
  'intArrayToString',
  'AsciiToString',
  'stringToAscii',
  'UTF16ToString',
  'stringToUTF16',
  'lengthBytesUTF16',
  'UTF32ToString',
  'stringToUTF32',
  'lengthBytesUTF32',
  'stringToNewUTF8',
  'stringToUTF8OnStack',
  'writeArrayToMemory',
  'registerKeyEventCallback',
  'maybeCStringToJsString',
  'findEventTarget',
  'getBoundingClientRect',
  'fillMouseEventData',
  'registerMouseEventCallback',
  'registerWheelEventCallback',
  'registerUiEventCallback',
  'registerFocusEventCallback',
  'fillDeviceOrientationEventData',
  'registerDeviceOrientationEventCallback',
  'fillDeviceMotionEventData',
  'registerDeviceMotionEventCallback',
  'screenOrientation',
  'fillOrientationChangeEventData',
  'registerOrientationChangeEventCallback',
  'fillFullscreenChangeEventData',
  'registerFullscreenChangeEventCallback',
  'JSEvents_requestFullscreen',
  'JSEvents_resizeCanvasForFullscreen',
  'registerRestoreOldStyle',
  'hideEverythingExceptGivenElement',
  'restoreHiddenElements',
  'setLetterbox',
  'softFullscreenResizeWebGLRenderTarget',
  'doRequestFullscreen',
  'fillPointerlockChangeEventData',
  'registerPointerlockChangeEventCallback',
  'registerPointerlockErrorEventCallback',
  'requestPointerLock',
  'fillVisibilityChangeEventData',
  'registerVisibilityChangeEventCallback',
  'registerTouchEventCallback',
  'fillGamepadEventData',
  'registerGamepadEventCallback',
  'registerBeforeUnloadEventCallback',
  'fillBatteryEventData',
  'registerBatteryEventCallback',
  'setCanvasElementSize',
  'getCanvasElementSize',
  'jsStackTrace',
  'getCallstack',
  'convertPCtoSourceLocation',
  'getEnvStrings',
  'checkWasiClock',
  'wasiRightsToMuslOFlags',
  'wasiOFlagsToMuslOFlags',
  'initRandomFill',
  'randomFill',
  'safeSetTimeout',
  'setImmediateWrapped',
  'safeRequestAnimationFrame',
  'clearImmediateWrapped',
  'registerPostMainLoop',
  'registerPreMainLoop',
  'getPromise',
  'makePromise',
  'idsToPromises',
  'makePromiseCallback',
  'ExceptionInfo',
  'findMatchingCatch',
  'Browser_asyncPrepareDataCounter',
  'isLeapYear',
  'ydayFromDate',
  'arraySum',
  'addDays',
  'getSocketFromFD',
  'getSocketAddress',
  'FS_createPreloadedFile',
  'FS_preloadFile',
  'FS_modeStringToFlags',
  'FS_getMode',
  'FS_stdin_getChar',
  'FS_mkdirTree',
  '_setNetworkCallback',
  'heapObjectForWebGLType',
  'toTypedArrayIndex',
  'webgl_enable_ANGLE_instanced_arrays',
  'webgl_enable_OES_vertex_array_object',
  'webgl_enable_WEBGL_draw_buffers',
  'webgl_enable_WEBGL_multi_draw',
  'webgl_enable_EXT_polygon_offset_clamp',
  'webgl_enable_EXT_clip_control',
  'webgl_enable_WEBGL_polygon_mode',
  'emscriptenWebGLGet',
  'computeUnpackAlignedImageSize',
  'colorChannelsInGlTextureFormat',
  'emscriptenWebGLGetTexPixelData',
  'emscriptenWebGLGetUniform',
  'webglGetUniformLocation',
  'webglPrepareUniformLocationsBeforeFirstUse',
  'webglGetLeftBracePos',
  'emscriptenWebGLGetVertexAttrib',
  '__glGetActiveAttribOrUniform',
  'writeGLArray',
  'registerWebGlEventCallback',
  'runAndAbortIfError',
  'ALLOC_NORMAL',
  'ALLOC_STACK',
  'allocate',
  'writeStringToMemory',
  'writeAsciiToMemory',
  'demangle',
  'stackTrace',
];
missingLibrarySymbols.forEach(missingLibrarySymbol)

  var unexportedSymbols = [
  'run',
  'out',
  'err',
  'callMain',
  'abort',
  'wasmMemory',
  'wasmExports',
  'HEAPF32',
  'HEAPF64',
  'HEAP8',
  'HEAPU8',
  'HEAP16',
  'HEAPU16',
  'HEAP32',
  'HEAPU32',
  'HEAP64',
  'HEAPU64',
  'writeStackCookie',
  'checkStackCookie',
  'INT53_MAX',
  'INT53_MIN',
  'bigintToI53Checked',
  'stackSave',
  'stackRestore',
  'ptrToString',
  'ENV',
  'ERRNO_CODES',
  'DNS',
  'Protocols',
  'Sockets',
  'timers',
  'warnOnce',
  'readEmAsmArgsArray',
  'wasmTable',
  'noExitRuntime',
  'addOnPreRun',
  'addOnPostRun',
  'freeTableIndexes',
  'functionsInTableMap',
  'setValue',
  'getValue',
  'PATH',
  'PATH_FS',
  'UTF8Decoder',
  'UTF8ArrayToString',
  'UTF8ToString',
  'UTF16Decoder',
  'JSEvents',
  'specialHTMLTargets',
  'findCanvasEventTarget',
  'currentFullscreenStrategy',
  'restoreOldWindowedStyle',
  'UNWIND_CACHE',
  'ExitStatus',
  'flush_NO_FILESYSTEM',
  'emSetImmediate',
  'emClearImmediate_deps',
  'emClearImmediate',
  'promiseMap',
  'uncaughtExceptionCount',
  'exceptionLast',
  'exceptionCaught',
  'Browser',
  'requestFullscreen',
  'requestFullScreen',
  'setCanvasSize',
  'getUserMedia',
  'createContext',
  'getPreloadedImageData__data',
  'wget',
  'MONTH_DAYS_REGULAR',
  'MONTH_DAYS_LEAP',
  'MONTH_DAYS_REGULAR_CUMULATIVE',
  'MONTH_DAYS_LEAP_CUMULATIVE',
  'SYSCALLS',
  'preloadPlugins',
  'FS_stdin_getChar_buffer',
  'FS_unlink',
  'FS_createPath',
  'FS_createDevice',
  'FS_readFile',
  'FS',
  'FS_root',
  'FS_mounts',
  'FS_devices',
  'FS_streams',
  'FS_nextInode',
  'FS_nameTable',
  'FS_currentPath',
  'FS_initialized',
  'FS_ignorePermissions',
  'FS_filesystems',
  'FS_syncFSRequests',
  'FS_readFiles',
  'FS_lookupPath',
  'FS_getPath',
  'FS_hashName',
  'FS_hashAddNode',
  'FS_hashRemoveNode',
  'FS_lookupNode',
  'FS_createNode',
  'FS_destroyNode',
  'FS_isRoot',
  'FS_isMountpoint',
  'FS_isFile',
  'FS_isDir',
  'FS_isLink',
  'FS_isChrdev',
  'FS_isBlkdev',
  'FS_isFIFO',
  'FS_isSocket',
  'FS_flagsToPermissionString',
  'FS_nodePermissions',
  'FS_mayLookup',
  'FS_mayCreate',
  'FS_mayDelete',
  'FS_mayOpen',
  'FS_checkOpExists',
  'FS_nextfd',
  'FS_getStreamChecked',
  'FS_getStream',
  'FS_createStream',
  'FS_closeStream',
  'FS_dupStream',
  'FS_doSetAttr',
  'FS_chrdev_stream_ops',
  'FS_major',
  'FS_minor',
  'FS_makedev',
  'FS_registerDevice',
  'FS_getDevice',
  'FS_getMounts',
  'FS_syncfs',
  'FS_mount',
  'FS_unmount',
  'FS_lookup',
  'FS_mknod',
  'FS_statfs',
  'FS_statfsStream',
  'FS_statfsNode',
  'FS_create',
  'FS_mkdir',
  'FS_mkdev',
  'FS_symlink',
  'FS_rename',
  'FS_rmdir',
  'FS_readdir',
  'FS_readlink',
  'FS_stat',
  'FS_fstat',
  'FS_lstat',
  'FS_doChmod',
  'FS_chmod',
  'FS_lchmod',
  'FS_fchmod',
  'FS_doChown',
  'FS_chown',
  'FS_lchown',
  'FS_fchown',
  'FS_doTruncate',
  'FS_truncate',
  'FS_ftruncate',
  'FS_utime',
  'FS_open',
  'FS_close',
  'FS_isClosed',
  'FS_llseek',
  'FS_read',
  'FS_write',
  'FS_mmap',
  'FS_msync',
  'FS_ioctl',
  'FS_writeFile',
  'FS_cwd',
  'FS_chdir',
  'FS_createDefaultDirectories',
  'FS_createDefaultDevices',
  'FS_createSpecialDirectories',
  'FS_createStandardStreams',
  'FS_staticInit',
  'FS_init',
  'FS_quit',
  'FS_findObject',
  'FS_analyzePath',
  'FS_createFile',
  'FS_createDataFile',
  'FS_forceLoadFile',
  'FS_createLazyFile',
  'FS_absolutePath',
  'FS_createFolder',
  'FS_createLink',
  'FS_joinPath',
  'FS_mmapAlloc',
  'FS_standardizePath',
  'MEMFS',
  'TTY',
  'PIPEFS',
  'SOCKFS',
  'tempFixedLengthArray',
  'miniTempWebGLFloatBuffers',
  'miniTempWebGLIntBuffers',
  'GL',
  'AL',
  'GLUT',
  'EGL',
  'GLEW',
  'IDBStore',
  'SDL',
  'SDL_gfx',
  'allocateUTF8',
  'allocateUTF8OnStack',
  'print',
  'printErr',
  'jstoi_s',
];
unexportedSymbols.forEach(unexportedRuntimeSymbol);

  // End runtime exports
  // Begin JS library exports
  // End JS library exports

// end include: postlibrary.js

function checkIncomingModuleAPI() {
  ignoredModuleProp('fetchSettings');
}
function proxy_convert_mp_to_js_then_js_to_mp_obj_jsside(out) { const ret = proxy_convert_mp_to_js_obj_jsside(out); proxy_convert_js_to_mp_obj_jsside_force_double_proxy(ret, out); }
function proxy_convert_mp_to_js_then_js_to_js_then_js_to_mp_obj_jsside(out) { const ret = proxy_convert_mp_to_js_obj_jsside(out); const js_obj = PyProxy.toJs(ret); proxy_convert_js_to_mp_obj_jsside(js_obj, out); }
function js_get_proxy_js_ref_info(out) { let used = 0; for (const elem of proxy_js_ref) { if (elem !== undefined) { ++used; } } Module.setValue(out, proxy_js_ref.length, "i32"); Module.setValue(out + 4, used, "i32"); }
function has_attr(jsref,str) { const base = proxy_js_ref[jsref]; const attr = UTF8ToString(str); if (attr in base) { return true; } else { return false; } }
function lookup_attr(jsref,str,out) { const base = proxy_js_ref[jsref]; const attr = UTF8ToString(str); let value = base[attr]; if (value !== undefined || attr in base) { proxy_convert_js_to_mp_obj_jsside(value, out); if (typeof value === "function" && !("_ref" in value)) { return 2; } else { return 1; } } else { return 0; } }
function store_attr(jsref,attr_ptr,value_ref) { const attr = UTF8ToString(attr_ptr); const value = proxy_convert_mp_to_js_obj_jsside(value_ref); proxy_js_ref[jsref][attr] = value; }
function call0(f_ref,out) { const f = proxy_js_ref[f_ref]; const ret = f(); proxy_convert_js_to_mp_obj_jsside(ret, out); }
function call1(f_ref,via_call,a0,out) { const a0_js = proxy_convert_mp_to_js_obj_jsside(a0); const f = proxy_js_ref[f_ref]; let ret; if (via_call) { ret = f.call(a0_js); } else { ret = f(a0_js); } proxy_convert_js_to_mp_obj_jsside(ret, out); }
function call2(f_ref,via_call,a0,a1,out) { const a0_js = proxy_convert_mp_to_js_obj_jsside(a0); const a1_js = proxy_convert_mp_to_js_obj_jsside(a1); const f = proxy_js_ref[f_ref]; let ret; if (via_call) { ret = f.call(a0_js, a1_js); } else { ret = f(a0_js, a1_js); } proxy_convert_js_to_mp_obj_jsside(ret, out); }
function calln(f_ref,via_call,n_args,value,out) { const f = proxy_js_ref[f_ref]; const a = []; for (let i = 0; i < n_args; ++i) { const v = proxy_convert_mp_to_js_obj_jsside(value + i * 3 * 4); a.push(v); } let ret; if (via_call) { ret = f.call(... a); } else { ret = f(... a); } proxy_convert_js_to_mp_obj_jsside(ret, out); }
function call0_kwarg(f_ref,via_call,n_kw,key,value,out) { const f = proxy_js_ref[f_ref]; const a = {}; for (let i = 0; i < n_kw; ++i) { const k = UTF8ToString(getValue(key + i * 4, "i32")); const v = proxy_convert_mp_to_js_obj_jsside(value + i * 3 * 4); a[k] = v; } let ret; if (via_call) { ret = f.call(a); } else { ret = f(a); } proxy_convert_js_to_mp_obj_jsside(ret, out); }
function call1_kwarg(f_ref,via_call,arg0,n_kw,key,value,out) { const f = proxy_js_ref[f_ref]; const a0 = proxy_convert_mp_to_js_obj_jsside(arg0); const a = {}; for (let i = 0; i < n_kw; ++i) { const k = UTF8ToString(getValue(key + i * 4, "i32")); const v = proxy_convert_mp_to_js_obj_jsside(value + i * 3 * 4); a[k] = v; } let ret; if (via_call) { ret = f.call(a0, a); } else { ret = f(a0, a); } proxy_convert_js_to_mp_obj_jsside(ret, out); }
function js_reflect_construct(f_ref,n_args,args,out) { const f = proxy_js_ref[f_ref]; const as = []; for (let i = 0; i < n_args; ++i) { as.push(proxy_convert_mp_to_js_obj_jsside(args + i * 3 * 4)); } const ret = Reflect.construct(f, as); proxy_convert_js_to_mp_obj_jsside(ret, out); }
function js_get_iter(f_ref,out) { const f = proxy_js_ref[f_ref]; const ret = f[Symbol.iterator](); proxy_convert_js_to_mp_obj_jsside(ret, out); }
function js_iter_next(f_ref,out) { const f = proxy_js_ref[f_ref]; const ret = f.next(); if (ret.done) { return false; } else { proxy_convert_js_to_mp_obj_jsside(ret.value, out); return true; } }
function js_subscr_load(f_ref,index_ref,out) { const target = proxy_js_ref[f_ref]; const index = python_index_semantics(target, proxy_convert_mp_to_js_obj_jsside(index_ref)); const ret = target[index]; proxy_convert_js_to_mp_obj_jsside(ret, out); }
function js_subscr_store(f_ref,idx,value) { const f = proxy_js_ref[f_ref]; f[proxy_convert_mp_to_js_obj_jsside(idx)] = proxy_convert_mp_to_js_obj_jsside(value); }
function proxy_js_free_obj(js_ref) { if (js_ref >= PROXY_JS_REF_NUM_STATIC) { proxy_js_ref_map.delete(proxy_js_ref[js_ref]); proxy_js_ref[js_ref] = undefined; if (js_ref < proxy_js_ref_next) { proxy_js_ref_next = js_ref; } } }
function js_check_existing(c_ref) { return proxy_js_check_existing(c_ref); }
function js_get_error_info(jsref,out_name,out_message) { const error = proxy_js_ref[jsref]; proxy_convert_js_to_mp_obj_jsside(error.name, out_name); proxy_convert_js_to_mp_obj_jsside(error.message, out_message); }
function js_then_resolve(ret_value,resolve) { const ret_value_js = proxy_convert_mp_to_js_obj_jsside(ret_value); const resolve_js = proxy_convert_mp_to_js_obj_jsside(resolve); resolve_js(ret_value_js); }
function js_then_reject(ret_value,reject) { let ret_value_js; try { ret_value_js = proxy_convert_mp_to_js_obj_jsside(ret_value); } catch(error) { ret_value_js = error; } const reject_js = proxy_convert_mp_to_js_obj_jsside(reject); reject_js(ret_value_js); }
function js_then_continue(jsref,py_resume,resolve,reject,out) { const py_resume_js = proxy_convert_mp_to_js_obj_jsside(py_resume); const resolve_js = proxy_convert_mp_to_js_obj_jsside(resolve); const reject_js = proxy_convert_mp_to_js_obj_jsside(reject); const ret = proxy_js_ref[jsref].then( (result) => { py_resume_js(result, null, resolve_js, reject_js); }, (reason) => { py_resume_js(null, reason, resolve_js, reject_js); }, ); proxy_convert_js_to_mp_obj_jsside(ret, out); }
function create_promise(out_set,out_promise) { const out_set_js = proxy_convert_mp_to_js_obj_jsside(out_set); const promise = new Promise(out_set_js); proxy_convert_js_to_mp_obj_jsside(promise, out_promise); }

// Imports from the Wasm binary.
var _fflush = makeInvalidEarlyAccess('_fflush');
var _strerror = makeInvalidEarlyAccess('_strerror');
var _emscripten_stack_get_end = makeInvalidEarlyAccess('_emscripten_stack_get_end');
var _emscripten_stack_get_base = makeInvalidEarlyAccess('_emscripten_stack_get_base');
var _setThrew = makeInvalidEarlyAccess('_setThrew');
var _emscripten_stack_init = makeInvalidEarlyAccess('_emscripten_stack_init');
var _emscripten_stack_get_free = makeInvalidEarlyAccess('_emscripten_stack_get_free');
var __emscripten_stack_restore = makeInvalidEarlyAccess('__emscripten_stack_restore');
var __emscripten_stack_alloc = makeInvalidEarlyAccess('__emscripten_stack_alloc');
var _emscripten_stack_get_current = makeInvalidEarlyAccess('_emscripten_stack_get_current');

function assignWasmExports(wasmExports) {
  _fflush = createExportWrapper('fflush', 1);
  _strerror = createExportWrapper('strerror', 1);
  _emscripten_stack_get_end = wasmExports['emscripten_stack_get_end'];
  _emscripten_stack_get_base = wasmExports['emscripten_stack_get_base'];
  _setThrew = createExportWrapper('setThrew', 2);
  _emscripten_stack_init = wasmExports['emscripten_stack_init'];
  _emscripten_stack_get_free = wasmExports['emscripten_stack_get_free'];
  __emscripten_stack_restore = wasmExports['_emscripten_stack_restore'];
  __emscripten_stack_alloc = wasmExports['_emscripten_stack_alloc'];
  _emscripten_stack_get_current = wasmExports['emscripten_stack_get_current'];
}
var wasmImports = {
  /** @export */
  fd_close: _fd_close,
  /** @export */
  fd_seek: _fd_seek,
  /** @export */
  fd_write: _fd_write
};


// include: postamble.js
// === Auto-generated postamble setup entry stuff ===

var calledRun;

function stackCheckInit() {
  // This is normally called automatically during __wasm_call_ctors but need to
  // get these values before even running any of the ctors so we call it redundantly
  // here.
  _emscripten_stack_init();
  // TODO(sbc): Move writeStackCookie to native to to avoid this.
  writeStackCookie();
}

function run() {

  stackCheckInit();

  preRun();

  function doRun() {
    // run may have just been called through dependencies being fulfilled just in this very frame,
    // or while the async setStatus time below was happening
    assert(!calledRun);
    calledRun = true;
    Module['calledRun'] = true;

    if (ABORT) return;

    initRuntime();

    readyPromiseResolve?.(Module);
    Module['onRuntimeInitialized']?.();
    consumedModuleProp('onRuntimeInitialized');

    assert(!Module['_main'], 'compiled without a main, but one is present. if you added it from JS, use Module["onRuntimeInitialized"]');

    postRun();
  }

  if (Module['setStatus']) {
    Module['setStatus']('Running...');
    setTimeout(() => {
      setTimeout(() => Module['setStatus'](''), 1);
      doRun();
    }, 1);
  } else
  {
    doRun();
  }
  checkStackCookie();
}

function checkUnflushedContent() {
  // Compiler settings do not allow exiting the runtime, so flushing
  // the streams is not possible. but in ASSERTIONS mode we check
  // if there was something to flush, and if so tell the user they
  // should request that the runtime be exitable.
  // Normally we would not even include flush() at all, but in ASSERTIONS
  // builds we do so just for this check, and here we see if there is any
  // content to flush, that is, we check if there would have been
  // something a non-ASSERTIONS build would have not seen.
  // How we flush the streams depends on whether we are in SYSCALLS_REQUIRE_FILESYSTEM=0
  // mode (which has its own special function for this; otherwise, all
  // the code is inside libc)
  var oldOut = out;
  var oldErr = err;
  var has = false;
  out = err = (x) => {
    has = true;
  }
  try { // it doesn't matter if it fails
    flush_NO_FILESYSTEM();
  } catch(e) {}
  out = oldOut;
  err = oldErr;
  if (has) {
    warnOnce('stdio streams had content in them that was not flushed. you should set EXIT_RUNTIME to 1 (see the Emscripten FAQ), or make sure to emit a newline when you printf etc.');
    warnOnce('(this may also be due to not including full filesystem support - try building with -sFORCE_FILESYSTEM)');
  }
}

var wasmExports;

// In modularize mode the generated code is within a factory function so we
// can use await here (since it's not top-level-await).
wasmExports = await (createWasm());

run();

// end include: postamble.js

// include: postamble_modularize.js
// In MODULARIZE mode we wrap the generated code in a factory function
// and return either the Module itself, or a promise of the module.
//
// We assign to the `moduleRtn` global here and configure closure to see
// this as and extern so it won't get minified.

if (runtimeInitialized)  {
  moduleRtn = Module;
} else {
  // Set up the promise that indicates the Module is initialized
  moduleRtn = new Promise((resolve, reject) => {
    readyPromiseResolve = resolve;
    readyPromiseReject = reject;
  });
}

// Assertion for attempting to access module properties on the incoming
// moduleArg.  In the past we used this object as the prototype of the module
// and assigned properties to it, but now we return a distinct object.  This
// keeps the instance private until it is ready (i.e the promise has been
// resolved).
for (const prop of Object.keys(Module)) {
  if (!(prop in moduleArg)) {
    Object.defineProperty(moduleArg, prop, {
      configurable: true,
      get() {
        abort(`Access to module property ('${prop}') is no longer possible via the module constructor argument; Instead, use the result of the module constructor.`)
      }
    });
  }
}
// end include: postamble_modularize.js



  return moduleRtn;
}

// Export using a UMD style export, or ES6 exports if selected
export default Module;

/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2023-2024 Damien P. George
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

// Options:
// - pystack: size in words of the MicroPython Python stack.
// - heapsize: size in bytes of the MicroPython GC heap.
// - url: location to load `micropython.mjs`.
// - stdin: function to return input characters.
// - stdout: function that takes one argument, and is passed lines of stdout
//   output as they are produced.  By default this is handled by Emscripten
//   and in a browser goes to console, in node goes to process.stdout.write.
// - stderr: same behaviour as stdout but for error output.
// - linebuffer: whether to buffer line-by-line to stdout/stderr.
export async function loadMicroPython(options) {
    const { pystack, heapsize, url, stdin, stdout, stderr, linebuffer } =
        Object.assign(
            { pystack: 2 * 1024, heapsize: 1024 * 1024, linebuffer: true },
            options,
        );
    let Module = {};
    Module.locateFile = (path, scriptDirectory) =>
        url || scriptDirectory + path;
    Module._textDecoder = new TextDecoder();
    if (stdin !== undefined) {
        Module.stdin = stdin;
    }
    if (stdout !== undefined) {
        if (linebuffer) {
            Module._stdoutBuffer = [];
            Module.stdout = (c) => {
                if (c === 10) {
                    stdout(
                        Module._textDecoder.decode(
                            new Uint8Array(Module._stdoutBuffer),
                        ),
                    );
                    Module._stdoutBuffer = [];
                } else {
                    Module._stdoutBuffer.push(c);
                }
            };
        } else {
            Module.stdout = (c) => stdout(new Uint8Array([c]));
        }
    }
    if (stderr !== undefined) {
        if (linebuffer) {
            Module._stderrBuffer = [];
            Module.stderr = (c) => {
                if (c === 10) {
                    stderr(
                        Module._textDecoder.decode(
                            new Uint8Array(Module._stderrBuffer),
                        ),
                    );
                    Module._stderrBuffer = [];
                } else {
                    Module._stderrBuffer.push(c);
                }
            };
        } else {
            Module.stderr = (c) => stderr(new Uint8Array([c]));
        }
    }
    Module = await _createMicroPythonModule(Module);
    globalThis.Module = Module;
    proxy_js_init();
    const pyimport = (name) => {
        const value = Module._malloc(3 * 4);
        Module.ccall(
            "mp_js_do_import",
            "null",
            ["string", "pointer"],
            [name, value],
        );
        return proxy_convert_mp_to_js_obj_jsside_with_free(value);
    };
    Module.ccall(
        "mp_js_init",
        "null",
        ["number", "number"],
        [pystack, heapsize],
    );
    Module.ccall("proxy_c_init", "null", [], []);
    return {
        _module: Module,
        PyProxy: PyProxy,
        FS: Module.FS,
        globals: {
            __dict__: pyimport("__main__").__dict__,
            get(key) {
                return this.__dict__[key];
            },
            set(key, value) {
                this.__dict__[key] = value;
            },
            delete(key) {
                delete this.__dict__[key];
            },
        },
        registerJsModule(name, module) {
            const value = Module._malloc(3 * 4);
            proxy_convert_js_to_mp_obj_jsside(module, value);
            Module.ccall(
                "mp_js_register_js_module",
                "null",
                ["string", "pointer"],
                [name, value],
            );
            Module._free(value);
        },
        pyimport: pyimport,
        runPython(code) {
            const len = Module.lengthBytesUTF8(code);
            const buf = Module._malloc(len + 1);
            Module.stringToUTF8(code, buf, len + 1);
            const value = Module._malloc(3 * 4);
            Module.ccall(
                "mp_js_do_exec",
                "number",
                ["pointer", "number", "pointer"],
                [buf, len, value],
            );
            Module._free(buf);
            return proxy_convert_mp_to_js_obj_jsside_with_free(value);
        },
        runPythonAsync(code) {
            const len = Module.lengthBytesUTF8(code);
            const buf = Module._malloc(len + 1);
            Module.stringToUTF8(code, buf, len + 1);
            const value = Module._malloc(3 * 4);
            Module.ccall(
                "mp_js_do_exec_async",
                "number",
                ["pointer", "number", "pointer"],
                [buf, len, value],
            );
            Module._free(buf);
            const ret = proxy_convert_mp_to_js_obj_jsside_with_free(value);
            if (ret instanceof PyProxyThenable) {
                return Promise.resolve(ret);
            }
            return ret;
        },
        replInit() {
            Module.ccall("mp_js_repl_init", "null", ["null"]);
        },
        replProcessChar(chr) {
            return Module.ccall(
                "mp_js_repl_process_char",
                "number",
                ["number"],
                [chr],
            );
        },
        // Needed if the GC/asyncify is enabled.
        async replProcessCharWithAsyncify(chr) {
            return Module.ccall(
                "mp_js_repl_process_char",
                "number",
                ["number"],
                [chr],
                { async: true },
            );
        },
    };
}

globalThis.loadMicroPython = loadMicroPython;

async function runCLI() {
    const fs = await import("fs");
    let heap_size = 128 * 1024;
    let contents = "";
    let repl = true;

    for (let i = 2; i < process.argv.length; i++) {
        if (process.argv[i] === "-X" && i < process.argv.length - 1) {
            if (process.argv[i + 1].includes("heapsize=")) {
                heap_size = parseInt(process.argv[i + 1].split("heapsize=")[1]);
                const suffix = process.argv[i + 1].substr(-1).toLowerCase();
                if (suffix === "k") {
                    heap_size *= 1024;
                } else if (suffix === "m") {
                    heap_size *= 1024 * 1024;
                }
                ++i;
            }
        } else {
            contents += fs.readFileSync(process.argv[i], "utf8");
            repl = false;
        }
    }

    if (process.stdin.isTTY === false) {
        contents = fs.readFileSync(0, "utf8");
        repl = false;
    }

    const mp = await loadMicroPython({
        heapsize: heap_size,
        stdout: (data) => process.stdout.write(data),
        linebuffer: false,
    });

    if (repl) {
        mp.replInit();
        process.stdin.setRawMode(true);
        process.stdin.on("data", (data) => {
            for (let i = 0; i < data.length; i++) {
                mp.replProcessCharWithAsyncify(data[i]).then((result) => {
                    if (result) {
                        process.exit();
                    }
                });
            }
        });
    } else {
        // If the script to run ends with a running of the asyncio main loop, then inject
        // a simple `asyncio.run` hook that starts the main task.  This is primarily to
        // support running the standard asyncio tests.
        if (contents.endsWith("asyncio.run(main())\n")) {
            const asyncio = mp.pyimport("asyncio");
            asyncio.run = async (task) => {
                await asyncio.create_task(task);
            };
        }

        try {
            mp.runPython(contents);
        } catch (error) {
            if (error.name === "PythonError") {
                if (error.type === "SystemExit") {
                    // SystemExit, this is a valid exception to successfully end a script.
                } else {
                    // An unhandled Python exception, print in out.
                    console.error(error.message);
                }
            } else {
                // A non-Python exception.  Re-raise it.
                throw error;
            }
        }
    }
}

// Check if Node is running (equivalent to ENVIRONMENT_IS_NODE).
if (
    typeof process === "object" &&
    typeof process.versions === "object" &&
    typeof process.versions.node === "string"
) {
    // Check if this module is run from the command line via `node micropython.mjs`.
    //
    // See https://stackoverflow.com/questions/6398196/detect-if-called-through-require-or-directly-by-command-line/66309132#66309132
    //
    // Note:
    // - `resolve()` is used to handle symlinks
    // - `includes()` is used to handle cases where the file extension was omitted when passed to node

    if (process.argv.length > 1) {
        const path = await import("path");
        const url = await import("url");

        const pathToThisFile = path.resolve(url.fileURLToPath(import.meta.url));
        const pathPassedToNode = path.resolve(process.argv[1]);
        const isThisFileBeingRunViaCLI =
            pathToThisFile.includes(pathPassedToNode);

        if (isThisFileBeingRunViaCLI) {
            runCLI();
        }
    }
}
/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2023-2024 Damien P. George
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

class PyProxy {
    constructor(ref) {
        this._ref = ref;
    }

    // Convert js_obj -- which is possibly a PyProxy -- to a JavaScript object.
    static toJs(js_obj) {
        if (!(js_obj instanceof PyProxy)) {
            return js_obj;
        }

        const type = Module.ccall(
            "proxy_c_to_js_get_type",
            "number",
            ["number"],
            [js_obj._ref],
        );

        if (type === 1 || type === 2) {
            // List or tuple.
            const array_ref = Module._malloc(2 * 4);
            const item = Module._malloc(3 * 4);
            Module.ccall(
                "proxy_c_to_js_get_array",
                "null",
                ["number", "pointer"],
                [js_obj._ref, array_ref],
            );
            const len = Module.getValue(array_ref, "i32");
            const items_ptr = Module.getValue(array_ref + 4, "i32");
            const js_array = [];
            for (let i = 0; i < len; ++i) {
                Module.ccall(
                    "proxy_convert_mp_to_js_obj_cside",
                    "null",
                    ["pointer", "pointer"],
                    [Module.getValue(items_ptr + i * 4, "i32"), item],
                );
                const js_item = proxy_convert_mp_to_js_obj_jsside(item);
                js_array.push(PyProxy.toJs(js_item));
            }
            Module._free(array_ref);
            Module._free(item);
            return js_array;
        }

        if (type === 3) {
            // Dict.
            const map_ref = Module._malloc(2 * 4);
            const item = Module._malloc(3 * 4);
            Module.ccall(
                "proxy_c_to_js_get_dict",
                "null",
                ["number", "pointer"],
                [js_obj._ref, map_ref],
            );
            const alloc = Module.getValue(map_ref, "i32");
            const table_ptr = Module.getValue(map_ref + 4, "i32");
            const js_dict = {};
            for (let i = 0; i < alloc; ++i) {
                const mp_key = Module.getValue(table_ptr + i * 8, "i32");
                if (mp_key > 8) {
                    // Convert key to JS object.
                    Module.ccall(
                        "proxy_convert_mp_to_js_obj_cside",
                        "null",
                        ["pointer", "pointer"],
                        [mp_key, item],
                    );
                    const js_key = proxy_convert_mp_to_js_obj_jsside(item);

                    // Convert value to JS object.
                    const mp_value = Module.getValue(
                        table_ptr + i * 8 + 4,
                        "i32",
                    );
                    Module.ccall(
                        "proxy_convert_mp_to_js_obj_cside",
                        "null",
                        ["pointer", "pointer"],
                        [mp_value, item],
                    );
                    const js_value = proxy_convert_mp_to_js_obj_jsside(item);

                    // Populate JS dict.
                    js_dict[js_key] = PyProxy.toJs(js_value);
                }
            }
            Module._free(map_ref);
            Module._free(item);
            return js_dict;
        }

        // Cannot convert to JS, leave as a PyProxy.
        return js_obj;
    }
}

// This handler's goal is to allow minimal introspection
// of Python references from the JS world/utilities.
const py_proxy_handler = {
    isExtensible() {
        return true;
    },
    ownKeys(target) {
        const value = Module._malloc(3 * 4);
        Module.ccall(
            "proxy_c_to_js_dir",
            "null",
            ["number", "pointer"],
            [target._ref, value],
        );
        const dir = proxy_convert_mp_to_js_obj_jsside_with_free(value);
        return PyProxy.toJs(dir).filter((attr) => !attr.startsWith("__"));
    },
    getOwnPropertyDescriptor(target, prop) {
        return {
            value: target[prop],
            enumerable: true,
            writable: true,
            configurable: true,
        };
    },
    has(target, prop) {
        // avoid throwing on `Symbol() in proxy` checks
        if (typeof prop !== "string") {
            // returns true only on iterator because other
            // symbols are not considered in the `get` trap
            return prop === Symbol.iterator;
        }
        return Module.ccall(
            "proxy_c_to_js_has_attr",
            "number",
            ["number", "string"],
            [target._ref, prop],
        );
    },
    get(target, prop) {
        if (prop === "_ref") {
            return target._ref;
        }

        // ignore both then and all symbols but Symbol.iterator
        if (prop === "then" || typeof prop !== "string") {
            if (prop === Symbol.iterator) {
                // Get the Python object iterator, and return a JavaScript generator.
                const iter_ref = Module.ccall(
                    "proxy_c_to_js_get_iter",
                    "number",
                    ["number"],
                    [target._ref],
                );
                return function* () {
                    const value = Module._malloc(3 * 4);
                    while (true) {
                        const valid = Module.ccall(
                            "proxy_c_to_js_iternext",
                            "number",
                            ["number", "pointer"],
                            [iter_ref, value],
                        );
                        if (!valid) {
                            break;
                        }
                        yield proxy_convert_mp_to_js_obj_jsside(value);
                    }
                    Module._free(value);
                };
            }
            return undefined;
        }

        const value = Module._malloc(3 * 4);
        Module.ccall(
            "proxy_c_to_js_lookup_attr",
            "null",
            ["number", "string", "pointer"],
            [target._ref, prop, value],
        );
        return proxy_convert_mp_to_js_obj_jsside_with_free(value);
    },
    set(target, prop, value) {
        const value_conv = Module._malloc(3 * 4);
        proxy_convert_js_to_mp_obj_jsside(value, value_conv);
        const ret = Module.ccall(
            "proxy_c_to_js_store_attr",
            "number",
            ["number", "string", "number"],
            [target._ref, prop, value_conv],
        );
        Module._free(value_conv);
        return ret;
    },
    deleteProperty(target, prop) {
        return Module.ccall(
            "proxy_c_to_js_delete_attr",
            "number",
            ["number", "string"],
            [target._ref, prop],
        );
    },
};

// PyProxy of a Python generator, that implements the thenable interface.
class PyProxyThenable {
    constructor(ref) {
        this._ref = ref;
    }

    then(resolve, reject) {
        const values = Module._malloc(3 * 3 * 4);
        proxy_convert_js_to_mp_obj_jsside(resolve, values + 3 * 4);
        proxy_convert_js_to_mp_obj_jsside(reject, values + 2 * 3 * 4);
        Module.ccall(
            "proxy_c_to_js_resume",
            "null",
            ["number", "pointer"],
            [this._ref, values],
        );
        return proxy_convert_mp_to_js_obj_jsside_with_free(values);
    }
}
/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2023-2024 Damien P. George
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

// Number of static entries at the start of proxy_js_ref.
const PROXY_JS_REF_NUM_STATIC = 2;

// These constants should match the constants in proxy_c.c.

const PROXY_KIND_MP_EXCEPTION = -1;
const PROXY_KIND_MP_NULL = 0;
const PROXY_KIND_MP_NONE = 1;
const PROXY_KIND_MP_BOOL = 2;
const PROXY_KIND_MP_INT = 3;
const PROXY_KIND_MP_FLOAT = 4;
const PROXY_KIND_MP_STR = 5;
const PROXY_KIND_MP_CALLABLE = 6;
const PROXY_KIND_MP_GENERATOR = 7;
const PROXY_KIND_MP_OBJECT = 8;
const PROXY_KIND_MP_JSPROXY = 9;
const PROXY_KIND_MP_EXISTING = 10;

const PROXY_KIND_JS_UNDEFINED = 0;
const PROXY_KIND_JS_NULL = 1;
const PROXY_KIND_JS_BOOLEAN = 2;
const PROXY_KIND_JS_INTEGER = 3;
const PROXY_KIND_JS_DOUBLE = 4;
const PROXY_KIND_JS_STRING = 5;
const PROXY_KIND_JS_OBJECT = 6;
const PROXY_KIND_JS_PYPROXY = 7;

class PythonError extends Error {
    constructor(exc_type, exc_details) {
        super(exc_details);
        this.name = "PythonError";
        this.type = exc_type;
    }
}

function proxy_js_init() {
    globalThis.proxy_js_ref = [globalThis, undefined];
    globalThis.proxy_js_ref_next = PROXY_JS_REF_NUM_STATIC;
    globalThis.proxy_js_ref_map = new Map();
    globalThis.proxy_js_map = new Map();
    globalThis.proxy_js_existing = [undefined];
    globalThis.pyProxyFinalizationRegistry = new FinalizationRegistry(
        (cRef) => {
            globalThis.proxy_js_map.delete(cRef);
            Module.ccall("proxy_c_free_obj", "null", ["number"], [cRef]);
        },
    );
}

// Check if the c_ref (Python proxy index) has a corresponding JavaScript-side PyProxy
// associated with it.  If so, take a concrete reference to this PyProxy from the WeakRef
// and put it in proxy_js_existing, to be referenced and reused by PROXY_KIND_MP_EXISTING.
function proxy_js_check_existing(c_ref) {
    const existing_obj = globalThis.proxy_js_map.get(c_ref)?.deref();
    if (existing_obj === undefined) {
        return -1;
    }

    // Search for a free slot in proxy_js_existing.
    for (let i = 0; i < globalThis.proxy_js_existing.length; ++i) {
        if (globalThis.proxy_js_existing[i] === undefined) {
            // Free slot found, put existing_obj here and return the index.
            globalThis.proxy_js_existing[i] = existing_obj;
            return i;
        }
    }

    // No free slot, so append to proxy_js_existing and return the new index.
    globalThis.proxy_js_existing.push(existing_obj);
    return globalThis.proxy_js_existing.length - 1;
}

// The `js_obj` argument cannot be `undefined`.
// Returns an integer reference to the given `js_obj`.
function proxy_js_add_obj(js_obj) {
    // See if there is an existing JsProxy reference, and use that if there is.
    const existing_ref = proxy_js_ref_map.get(js_obj);
    if (existing_ref !== undefined) {
        return existing_ref;
    }

    // Search for the first free slot in proxy_js_ref.
    while (proxy_js_ref_next < proxy_js_ref.length) {
        if (proxy_js_ref[proxy_js_ref_next] === undefined) {
            // Free slot found, reuse it.
            const id = proxy_js_ref_next;
            ++proxy_js_ref_next;
            proxy_js_ref[id] = js_obj;
            proxy_js_ref_map.set(js_obj, id);
            return id;
        }
        ++proxy_js_ref_next;
    }

    // No free slots, so grow proxy_js_ref by one (append at the end of the array).
    const id = proxy_js_ref.length;
    proxy_js_ref[id] = js_obj;
    proxy_js_ref_next = proxy_js_ref.length;
    proxy_js_ref_map.set(js_obj, id);
    return id;
}

function proxy_call_python(target, argumentsList) {
    let args = 0;

    // Strip trailing "undefined" arguments.
    while (
        argumentsList.length > 0 &&
        argumentsList[argumentsList.length - 1] === undefined
    ) {
        argumentsList.pop();
    }

    if (argumentsList.length > 0) {
        // TODO use stackAlloc/stackRestore?
        args = Module._malloc(argumentsList.length * 3 * 4);
        for (const i in argumentsList) {
            proxy_convert_js_to_mp_obj_jsside(
                argumentsList[i],
                args + i * 3 * 4,
            );
        }
    }
    const value = Module._malloc(3 * 4);
    Module.ccall(
        "proxy_c_to_js_call",
        "null",
        ["number", "number", "number", "pointer"],
        [target, argumentsList.length, args, value],
    );
    if (argumentsList.length > 0) {
        Module._free(args);
    }
    const ret = proxy_convert_mp_to_js_obj_jsside_with_free(value);
    if (ret instanceof PyProxyThenable) {
        // In Python when an async function is called it creates the
        // corresponding "generator", which must then be executed at
        // the top level by an asyncio-like scheduler.  In JavaScript
        // the semantics for async functions is that they are started
        // immediately (their non-async prefix code is executed immediately)
        // and only if they await do they return a Promise to delay the
        // execution of the remainder of the function.
        //
        // Emulate the JavaScript behaviour here by resolving the Python
        // async function.  We assume that the caller who gets this
        // return is JavaScript.
        return Promise.resolve(ret);
    }
    return ret;
}

function proxy_convert_js_to_mp_obj_jsside(js_obj, out) {
    let kind;
    if (js_obj === undefined) {
        kind = PROXY_KIND_JS_UNDEFINED;
    } else if (js_obj === null) {
        kind = PROXY_KIND_JS_NULL;
    } else if (typeof js_obj === "boolean") {
        kind = PROXY_KIND_JS_BOOLEAN;
        Module.setValue(out + 4, js_obj, "i32");
    } else if (typeof js_obj === "number") {
        if (Number.isInteger(js_obj)) {
            kind = PROXY_KIND_JS_INTEGER;
            Module.setValue(out + 4, js_obj, "i32");
        } else {
            kind = PROXY_KIND_JS_DOUBLE;
            // double must be stored to an address that's a multiple of 8
            const temp = (out + 4) & ~7;
            Module.setValue(temp, js_obj, "double");
            const double_lo = Module.getValue(temp, "i32");
            const double_hi = Module.getValue(temp + 4, "i32");
            Module.setValue(out + 4, double_lo, "i32");
            Module.setValue(out + 8, double_hi, "i32");
        }
    } else if (typeof js_obj === "string") {
        kind = PROXY_KIND_JS_STRING;
        const len = Module.lengthBytesUTF8(js_obj);
        const buf = Module._malloc(len + 1);
        Module.stringToUTF8(js_obj, buf, len + 1);
        Module.setValue(out + 4, len, "i32");
        Module.setValue(out + 8, buf, "i32");
    } else if (
        js_obj instanceof PyProxy ||
        (typeof js_obj === "function" && "_ref" in js_obj) ||
        js_obj instanceof PyProxyThenable
    ) {
        kind = PROXY_KIND_JS_PYPROXY;
        Module.setValue(out + 4, js_obj._ref, "i32");
    } else {
        kind = PROXY_KIND_JS_OBJECT;
        const id = proxy_js_add_obj(js_obj);
        Module.setValue(out + 4, id, "i32");
    }
    Module.setValue(out + 0, kind, "i32");
}

function proxy_convert_js_to_mp_obj_jsside_force_double_proxy(js_obj, out) {
    if (
        js_obj instanceof PyProxy ||
        (typeof js_obj === "function" && "_ref" in js_obj) ||
        js_obj instanceof PyProxyThenable
    ) {
        const kind = PROXY_KIND_JS_OBJECT;
        const id = proxy_js_add_obj(js_obj);
        Module.setValue(out + 4, id, "i32");
        Module.setValue(out + 0, kind, "i32");
    } else {
        proxy_convert_js_to_mp_obj_jsside(js_obj, out);
    }
}

function proxy_convert_mp_to_js_obj_jsside(value) {
    const kind = Module.getValue(value, "i32");
    let obj;
    if (kind === PROXY_KIND_MP_EXCEPTION) {
        // Exception
        const str_len = Module.getValue(value + 4, "i32");
        const str_ptr = Module.getValue(value + 8, "i32");
        const str = Module.UTF8ToString(str_ptr, str_len);
        Module._free(str_ptr);
        const str_split = str.split("\x04");
        throw new PythonError(str_split[0], str_split[1]);
    }
    if (kind === PROXY_KIND_MP_NULL) {
        // MP_OBJ_NULL
        throw new Error("NULL object");
    }
    if (kind === PROXY_KIND_MP_NONE) {
        // None
        obj = null;
    } else if (kind === PROXY_KIND_MP_BOOL) {
        // bool
        obj = Module.getValue(value + 4, "i32") ? true : false;
    } else if (kind === PROXY_KIND_MP_INT) {
        // int
        obj = Module.getValue(value + 4, "i32");
    } else if (kind === PROXY_KIND_MP_FLOAT) {
        // float
        // double must be loaded from an address that's a multiple of 8
        const temp = (value + 4) & ~7;
        const double_lo = Module.getValue(value + 4, "i32");
        const double_hi = Module.getValue(value + 8, "i32");
        Module.setValue(temp, double_lo, "i32");
        Module.setValue(temp + 4, double_hi, "i32");
        obj = Module.getValue(temp, "double");
    } else if (kind === PROXY_KIND_MP_STR) {
        // str
        const str_len = Module.getValue(value + 4, "i32");
        const str_ptr = Module.getValue(value + 8, "i32");
        obj = Module.UTF8ToString(str_ptr, str_len);
    } else if (kind === PROXY_KIND_MP_JSPROXY) {
        // js proxy
        const id = Module.getValue(value + 4, "i32");
        obj = proxy_js_ref[id];
    } else if (kind === PROXY_KIND_MP_EXISTING) {
        const id = Module.getValue(value + 4, "i32");
        obj = globalThis.proxy_js_existing[id];
        globalThis.proxy_js_existing[id] = undefined;
    } else {
        // obj
        const id = Module.getValue(value + 4, "i32");
        if (kind === PROXY_KIND_MP_CALLABLE) {
            obj = (...args) => {
                return proxy_call_python(id, args);
            };
            obj._ref = id;
        } else if (kind === PROXY_KIND_MP_GENERATOR) {
            obj = new PyProxyThenable(id);
        } else {
            // PROXY_KIND_MP_OBJECT
            const target = new PyProxy(id);
            obj = new Proxy(target, py_proxy_handler);
        }
        globalThis.pyProxyFinalizationRegistry.register(obj, id);
        globalThis.proxy_js_map.set(id, new WeakRef(obj));
    }
    return obj;
}

function proxy_convert_mp_to_js_obj_jsside_with_free(value) {
    const ret = proxy_convert_mp_to_js_obj_jsside(value);
    Module._free(value);
    return ret;
}

function python_index_semantics(target, index_in) {
    let index = index_in;
    if (typeof index === "number") {
        if (index < 0) {
            index += target.length;
        }
        if (index < 0 || index >= target.length) {
            throw new PythonError("IndexError", "index out of range");
        }
    }
    return index;
}
