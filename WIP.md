

 - [ ] class NeoPixel: - indexing
        https://github.com/Josverl/micropython-stubs/issues/764

        ERROR    root:typecheck.py:171 "tests/quality_tests/check_rp2/check_neopixel.py"(10,0): "__setitem__" method not defined on type "NeoPixel"
        ERROR    root:typecheck.py:171 "tests/quality_tests/check_rp2/check_neopixel.py"(12,10): "__getitem__" method not defined on type "NeoPixel"

 - [ ] mod:socket - missing module constants 
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_micropython/check_functions.py"(5,7): "AF_INET" is not defined
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_micropython/check_functions.py"(5,16): "SOCK_STREAM" is not defined
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_micropython/check_functions.py"(7,7): "AF_INET" is not defined
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_micropython/check_functions.py"(7,16): "SOCK_DGRAM" is not defined

- [ ] uasyncio.Task 
        subclass : 
            class Task(futures._PyFuture):
        methods : 
        - cancel
        - __await__
        - s.read()  / __call__ ?>?


        INFO     root:typecheck.py:175 "tests/quality_tests/feat_uasyncio/check_demo/aiorepl.py"(67,26): Cannot access attribute "cancel" for class "Task"
        Attribute "cancel" is unknown
        INFO     root:typecheck.py:175 "tests/quality_tests/feat_uasyncio/check_demo/aiorepl.py"(69,26): "Task" is not awaitable
        "Task" is incompatible with protocol "Awaitable[_T_co@Awaitable]"
            "__await__" is not present

- [ ] # TODO: fix type stubs asyncio.StreamReader
        ```python

            awritestr: Generator  ## = <generator>
            wait_closed: Generator  ## = <generator>
            drain: Generator  ## = <generator>
            readexactly: Generator  ## = <generator>
            readinto: Generator  ## = <generator>
            awrite: Generator  ## = <generator>
            readline: Generator  ## = <generator>
            aclose: Generator  ## = <generator>

            # read: Generator  ## = <generator>
            async def read(self, n=-1):
                """Read up to `n` bytes from the stream.
                
                If `n` is not provided or set to -1,
                read until EOF, then return all read bytes.
                If EOF was received and the internal buffer is empty,
                return an empty bytes object.

                If `n` is 0, return an empty bytes object immediately.

                If `n` is positive, return at most `n` available bytes
                as soon as at least 1 byte is available in the internal buffer.
                If EOF is received before any byte is read, return an empty
                bytes object.

                Returned value is not limited with limit, configured at stream
                creation.

                If stream was paused, this function will automatically resume it if
                needed.
                """

        ```

 - [ ] stdib - io 
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_stdlib/check_io.py"(11,9): "BufferedWriter" is not a known attribute of module "io"
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_stdlib/check_json/check_json.py"(38,26): No parameter named "separators"
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_stdlib/check_os/check_files.py"(40,29): Type "str | list[dict[Unknown, Unknown]]" is not assignable to declared type "List[str]"
    Type "str | list[dict[Unknown, Unknown]]" is not assignable to type "List[str]"
        "str" is not assignable to "List[str]"
    INFO     root:typecheck.py:175 "tests/quality_tests/feat_stdlib/check_os/check_files.py"(56,24): Type of "subdir" is "List[str]"
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_stdlib/check_os/check_files.py"(57,17): Type "list[str | dict[Unknown, Unknown]]" is not assignable to declared type "List[dict[Unknown, Unknown]]"
    "list[str | dict[Unknown, Unknown]]" is not assignable to "List[dict[Unknown, Unknown]]"
        Type parameter "_T@list" is invariant, but "str | dict[Unknown, Unknown]" is not the same as "dict[Unknown, Unknown]"
        Consider switching from "list" to "Sequence" which is covariant
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_stdlib/check_os/check_uname.py"(19,12): "assert_type" mismatch: expected "str" but received "str | Unknown"
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_stdlib/check_os/check_uname.py"(20,12): "assert_type" mismatch: expected "str" but received "str | Unknown"
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_stdlib/check_os/check_uname.py"(21,12): "assert_type" mismatch: expected "str" but received "str | Unknown"
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_stdlib/check_os/check_uname.py"(22,12): "assert_type" mismatch: expected "str" but received "str | Unknown"
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_stdlib/check_os/check_uname.py"(23,12): "assert_type" mismatch: expected "str" but received "str | Unknown"
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_stdlib/check_sys/check_sys.py"(24,20): Argument of type "exc" cannot be assigned to parameter "exc" of type "BaseException" in function "print_exception"



 - [ ] Disable ruff warnings 
        - UP015, UP031, UP032

