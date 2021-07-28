""" Work in Progress  
Tries to determine the return type by parsing the docstring 
 - use re to find phrases such as:
    - 'Returns ..... '
    - 'Gets  ..... '
 - then parses the resulting sentences to find references to known types and gives then a rating 
 - builds a list return type candidates 
 - selects the highest ranking candidate 
 - the default Type is 'Any'

todo: 
    - filter out obvious wrong types ( deny-list) 
    - also pass in the function/method/class defenition as that may/SHOULD contain the return type, in which case that should take precedence
    - build test and  % report 
    - 
"""
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

    if any(num in my_type for num in ("unsigned integer", "unsigned int", "unsigned")):
        # Assume unsigned are uint
        result = base.copy()
        result["type"] = "uint"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

    if any(
        num in my_type
        for num in (
            "number",
            "integer",
            "count",
            " int ",
            "length",
            "index",
            "**signed** value",
            "0 or 1",
        )
    ):
        # Assume numbers are signed int
        result = base.copy()
        result["type"] = "int"
        result["confidence"] = 0.7  # OK
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
        for t in (
            "float",
            "logarithm",
            "sine",
            "tangent",
            "exponential",
            "complex number",
            "phase",
        )
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

    if any(t in my_type for t in ("``None``", "None")):
        result = base.copy()
        result["type"] = "None"
        result["confidence"] = 0.8  # OK
        candidates.append(result)

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
            if object in ("stream-like", "file"):
                object = "stream"
            elif object == "callback":
                object = "Callable[..., Any]"
                # todo: requires additional 'from typing import Callable'

            # clean
            object = re.sub(r"[^a-z.A-Z0-9]", "", object)
            result = base.copy()
            result["type"] = object
            if object[0].isupper():
                result["confidence"] = 0.8  # Good
            else:
                result["confidence"] = 0.3  # not so good

            candidates.append(result)

    if " " in my_type:
        result = base.copy()
        result = {"type": "Any", "confidence": 0.2}
        candidates.append(result)
    elif my_type[0].isdigit() or len(my_type) < 3 or my_type in ("them", "the", "immediately"):
        # avoid short words, starts with digit, or a few detected
        result = base.copy()
        result = {"type": "Any", "confidence": 0.2}
        candidates.append(result)

    else:

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

                    isGood = r["confidence"] >= 0.5 and r["confidence"] <= 0.8 and item[2] != ""
                    isBad = r["confidence"] <= 0.5 and r["confidence"] <= 0.8 and item[2] != ""
                    if isBad:

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
