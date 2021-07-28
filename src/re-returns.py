# ref: https://regex101.com/codegen?language=python
# https://regex101.com/r/D5ddB2/1


import json
from pathlib import Path
import re
from typing import Dict, List, Tuple, Union


def distill_return(return_text: str) -> List[Dict]:
    "find return text and confidence"
    candidates = []
    base = {"type": "Any", "confidence": 0, "match": None}
    # clean up my_type
    my_type = return_text.strip().rstrip(".")
    my_type = my_type.replace("`", "")

    # print(my_type)
    if any(t in my_type for t in ("a list of", "list of", "an array")):
        # Lists of Any / Tuple
        lt = "Any"
        result = base.copy()
        result["confidence"] = 0.8  # OK
        for element in ("tuple", "string", "int"):
            if element in my_type:
                lt = element
                result["confidence"] = 0.9  # GOOD

        my_type = f"List[{lt}]"
        result["type"] = my_type
        candidates.append(result)

    if any(t in my_type for t in ("a dictionary", "dict")):
        # Lists of Any / Tuple
        lt = "Any"
        result = base.copy()
        result["confidence"] = 0.8  # OK
        if "tuple" in my_type:
            lt = "Tuple"
            result["confidence"] = 0.9  # GOOD
        my_type = f"Dict[{lt}]"
        result["type"] = my_type
        candidates.append(result)

    if any(t in my_type for t in ("tuple", "a pair")):
        result = base.copy()
        result["type"] = "tuple"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

        # tuple ?
        # usocket.socket.socket.recvfrom           bytes           - 0.8 ('value is a pair *(bytes, address)* where *bytes* is a',)
        # usocket.socket.socket.accept             Any             - 0.2 ('value is a pair (conn, address) where conn is a new socket object usable to send',)
        # uasyncio.Lock.Lock.release               Any             - 0.2 ('a pair of streams: a reader and a writer stream.',)
    if any(num in my_type for num in ("number", "integer", "count", " int ", "length", "index")):
        # Assume numbers are number
        result = base.copy()
        result["type"] = "int"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(t in my_type for t in ("bytearray",)):
        result = base.copy()
        result["type"] = "bytearray"
        result["confidence"] = 0.85  # better match than bytes
        candidates.append(result)

    if any(t in my_type for t in ("bytes",)):
        result = base.copy()
        result["type"] = "bytes"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(t in my_type for t in ("boolean", "True", "False")):
        result = base.copy()
        result["type"] = "boolean"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(
        t in my_type
        for t in ("float", "logarithm", "sine", "tangent", "exponential", "complex number", "phase")
    ):
        result = base.copy()
        result["type"] = "float"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(t in my_type for t in ("string",)):
        result = base.copy()
        result["type"] = "str"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(t in my_type for t in ("``None``",)):
        result = base.copy()
        result["type"] = "None"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    # signed int
    # ===========
    # utime..ticks_add                         Any             - 0.2 ('**signed** value in the range',)
    # esp32.NVS.NVS.get_i32                    int             - 0.8 ('the signed integer value for the specified key. Raises an OSError if the key does not',)

    if any(t in my_type for t in ("Object", "object")):
        words = my_type.split(" ")
        try:
            i = words.index("Object")
        except ValueError:
            try:
                i = words.index("object")
            except ValueError:
                # object is not a word, but is a part of a word
                i = 0

        if i > 0:
            object = words[i - 1]
            if object == "stream-like":
                object = "stream"

            # clean
            object = re.sub(r"[^a-z.A-Z0-9]", "", object)
            result = base.copy()
            result["type"] = object
            if object[0].isupper():
                result["confidence"] = 0.8  # OK
            else:
                result["confidence"] = 0.6  # OK

            candidates.append(result)

    # Object
    # ===========
    #                                                                ('a file object associated with the socket)
    # ure..                                    Any             - 0.2 ('`regex <regex>` object',)
    # network.WLANWiPy.WLANWiPy.irq            Any             - 0.2 ('an IRQ object',)
    # network.CC3K.                            Any             - 0.2 ('the CC3K object.',)
    # pyb..mount                               Any             - 0.2 ('or set the UART object where the REPL is repeated on',)
    # pyb.pyb.Accel.                           Any             - 0.2 ('an accelerometer object',)
    # rp2.StateMachine.StateMachine.irq        Any             - 0.2 ('the IRQ object for the given StateMachine.',)
    # uasyncio..open_connection                Any             - 0.2 ('a `Server` object.',)
    # ujson..load                              Any             - 0.2 ('an object.  Raises :exc:`ValueError` if the',)

    # Iterator
    # ========
    # uselect.poll.poll.ipoll                  Any             - 0.2 ('an iterator which yields a',)

    if " " in my_type:
        result = base.copy()
        result = {"type": "Any", "confidence": 0.2}
        candidates.append(result)
    else:
        # TODO : Sanity check
        # prevent simple words
        # =====================
        # esp32.Partition.Partition.find           a               - 0.5 ('a',)
        # esp32.RMT.RMT.source_freq                80MHz           - 0.5 ('80MHz',)
        # pyb.pinaf.pinaf.reg                      stm             - 0.5 ('stm',)
        # pyb.UART.UART.readline                   is              - 0.5 ('is',)
        # pyb.USB_VCP.USB_VCP.read                 immediately     - 0.5 ('immediately',)
        # uasyncio.Event.Event.wait                immediately     - 0.5 ('    immediately.',)
        # uasyncio.Stream.Stream.read              them            - 0.5 ('them.',)
        # uasyncio.Stream.Stream.readline          it              - 0.5 ('it.',)
        # ubluetooth.BLE.BLE.active                the             - 0.5 ('the',)
        assert not " " in my_type
        assert not ":" in my_type
        result = base.copy()
        result["type"] = my_type
        result["confidence"] = 0.1  # medium
        candidates.append(result)
    return candidates


def type_from_docstring(docstring: Union[str, List[str]]):

    if isinstance(docstring, list):
        docstring = "\n".join(docstring)
    return_regex = r"Return(?:s?|(?:ing)?)\s(?!information)(?P<return>.*)[.|$|\s]"
    gets_regex = r"Gets?\s(?P<return>.*)[.|$|\s]"

    matches: List[re.Match] = []
    candidates: List[Dict] = []

    for regex in (return_regex, gets_regex):
        match_iter = re.finditer(regex, docstring, re.MULTILINE | re.IGNORECASE)
        for match in match_iter:
            # matches.append(match)
            distilled = distill_return(match.group("return"))
            for item in distilled:
                candidate = {
                    "match": match,
                    "type": item["type"],
                    "confidence": item["confidence"],
                }
                candidates.append(candidate)
    # Sort
    # print(candidates)
    if len(candidates) > 0:
        candidates = sorted(candidates, key=lambda x: x["confidence"], reverse=True)
        # print(candidates[0])
        return candidates[0]  # best candidate
    else:
        return {"type": "Any", "confidence": 0, "match": None}


def process(pattern: str):

    folder = Path("generated/micropython/1_16-nightly")
    # read all .json files in the folder
    for file in folder.glob(pattern):
        with open(file, errors="ignore", encoding="utf8") as fp:
            # read docstrings from json
            docstrings: List[Tuple] = json.load(fp)
            for item in docstrings:
                if item[3] != []:
                    r = type_from_docstring(item[3])
                    # print("{0}, {1}".format(*item))
                    if r["confidence"] >= 0.5 and r["confidence"] <= 0.8 and item[2] != "":
                        context = ".".join((item[0], item[1], item[2]))
                        try:
                            print(
                                f"{context:40} {r['type']:<15} - {r['confidence']} {r['match'].groups('return')}"
                            )
                        except:
                            print(f"{context:40} {r['type']:<15} - {r['confidence']} ")

                        # print(r)


if __name__ == "__main__":
    process("*.json")
    # sample_authentication_with_api_key_credential()
