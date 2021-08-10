""" Work in Progress  

Tries to determine the return type by parsing the docstring and the function signature
 - if the signature contains a return type --> <something> then that is returned
 - check a lookup dictionary of type overrides, 
    if the functionnae is listed, then use the override
 - use re to find phrases such as:
    - 'Returns ..... '
    - 'Gets  ..... '
 - docstring is joined without newlines to simplify parsing
 - then parses the docstring to find references to known types and give then a rating though a hand coded model ()
 - builds a list return type candidates 
 - selects the highest ranking candidate 
 - the default Type is 'Any'
 

todo: 

    - regex :
        - 'With no arguments the frequency in Hz is returned.'
        - 'Get or set' --> indicates overloaded/optional return Union[None|...]
        - add regex for 'Query' ` Otherwise, query current state if no argument is provided. `

    - regex :
        - 'With no arguments the frequency in Hz is returned.'
        - 'Get or set' --> indicates overloaded/optional return Union[None|...]
        - add regex for 'Query' ` Otherwise, query current state if no argument is provided. `

    - try if an Azure Machine Learning works as well 
        https://docs.microsoft.com/en-us/azure/machine-learning/quickstart-create-resources
    - 
"""
# ref: https://regex101.com/codegen?language=python
# https://regex101.com/r/Ni8g2z/2

import logging
import re
from typing import Dict, List, Tuple, Union
from rst_lookup import LOOKUP_LIST

# logging
log = logging.getLogger(__name__)

# all possibles
TYPING_IMPORT = "from typing import Any, Dict, IO, List, Optional, Tuple, Union, NoReturn, Generator, Iterator, Callable\n"
BASE = {"type": "Any", "confidence": 0, "match": None}


def dist_rate(i) -> float:
    """"""
    max_len = 150  # must occur in the first 150 chars
    linear = max((max_len - i), 1) / max_len
    # quadratic = max(max_len - (i / 18) ** 4, 1) / max_len
    return linear


def simple_candidates(
    type: str,
    my_type: str,
    keywords: List[str],
    rate: float = 0.5,
    exclude: List[str] = [],
):
    """
    find and rate possible types and confidence weighting for simple types.
    Case sensitive
    """
    candidates = []
    if not any(t in my_type for t in keywords) or any(t in my_type for t in exclude):
        # quick bailout , there are no matches, or there is an exclude
        return []
    for kw in keywords:
        i = my_type.find(kw)
        if i < 0:
            continue
        # Assume unsigned are uint
        result = BASE.copy()
        result["type"] = type
        result["confidence"] = rate * dist_rate(i)  # OK
        log.info(f" - found '{kw}' at position {i} with rating {dist_rate(i)}")
        candidates.append(result)
    return candidates


def compound_candidates(
    type: str,
    my_type: str,
    keywords: List[str],
    rate: float = 0.85,
    exclude: List[str] = [],
):
    """
    find and rate possible types and confidence weighting for compound types that can have a subscription.
    Case sensitive
    """
    candidates = []
    if not any(t in my_type for t in keywords) or any(t in my_type for t in exclude):
        # quick bailout , there are no matches, or there is an exclude
        return []
    for kw in keywords:
        i = my_type.find(kw)
        if i < 0:
            continue
        # List / Dict / Generator of Any / Tuple /
        sub = None
        result = BASE.copy()
        confidence = rate
        for element in ("tuple", "string", "unsigned", "int"):
            if element in my_type.casefold():
                j = my_type.find(element)
                if i == j:
                    # do not match on the same main and sub
                    continue
                confidence += 0.10  # boost as we have a subtype
                if element == "tuple":
                    sub = "Tuple"
                    break
                elif element == "string":
                    sub = "str"
                    break
                elif element == "unsigned":
                    sub = "uint"
                    break
                else:
                    lt = element
        if sub:
            result["type"] = f"{type}[{sub}]"
        else:
            result["type"] = f"{type}"
        confidence = confidence * dist_rate(i)  # distance weighting
        result["confidence"] = confidence
        log.info(
            f" - found '{kw}' at position {i} with confidence {confidence} rating {dist_rate(i)}"
        )

        candidates.append(result)
    return candidates


def object_candidates(
    my_type: str,
    rate: float = 0.81,
    exclude: List[str] = [],
):
    """
    find and rate possible types and confidence weighting for Object types.
    Case sensitive
    """

    candidates = []
    keywords = [
        "Object",
        "object",
    ]  # Q&D

    if not any(t in my_type for t in keywords) or any(t in my_type for t in exclude):
        # quick bailout , there are no matches, or there is an exclude
        return []
    for kw in keywords:
        i = my_type.find(kw)
        if i < 0:
            continue
        # List / Dict / Generator of Any / Tuple /
        sub = None
        result = BASE.copy()
        confidence = rate

        # did the word actually occur, or is it just a partial
        words = my_type.split(" ")  # Return <multiple words object>
        if kw in words:
            pos = words.index(kw)
            if pos == 0:
                object = "Any"
            else:
                object = words[pos - 1]
            if object in ("stream-like", "file"):
                object = "IO"  # needs from typing import IO
            elif object == "callback":
                object = "Callable[..., Any]"
                # todo: requires additional 'from typing import Callable'
            else:
                # clean
                object = re.sub(r"[^a-z.A-Z0-9]", "", object)
            result = BASE.copy()
            result["type"] = object
            if object == "an":  # "Return an object"
                result["type"] = "Any"
                confidence += 0.10  # abstract , but very good
            elif object[0].islower():
                confidence -= 0.20  # not so good
            result["confidence"] = confidence * dist_rate(i)
            candidates.append(result)
    return candidates


def distill_return(return_text: str) -> List[Dict]:
    """Find return type and confidence.
    Returns a list of possible types and confidence weighting.
        {
            type :str               # the return type
            confidence: float       # the confidence between 0.0 and 1
            match: Optional[str]    # for debugging : the reason the match was made
          }

    """
    candidates = [BASE]  # Default to the base , which is 'Any'

    # clean up my_type
    my_type = return_text.strip().rstrip(".")
    my_type = my_type.replace("`", "")

    candidates += compound_candidates("Generator", my_type, ["generator"], 0.85)
    candidates += compound_candidates("Iterator", my_type, ["iterator"], 0.85)
    candidates += compound_candidates("List", my_type, ["a list of", "list of", "an array"], 0.80)

    candidates += simple_candidates("Dict", my_type, ["a dictionary", "dict"], 0.80)
    candidates += simple_candidates("Tuple", my_type, ["tuple", "a pair"], 0.80)

    candidates += simple_candidates(
        "uint", my_type, ["unsigned integer", "unsigned int", "unsigned"], 0.84
    )

    candidates += simple_candidates(
        "int",
        my_type,
        [
            "number",
            "integer",
            "count",
            " int ",
            "0 or 1",
        ],
        0.83,
    )

    # good but nor perfect indicators of integers
    candidates += simple_candidates(
        "int",
        my_type,
        [
            "length",
            "total size",
            "size of",
            "the index",
        ],
        0.95,
    )

    # Assume numbers are signed int
    candidates += simple_candidates(
        "int",
        my_type,
        [
            "index",
            "**signed** value",
            "nanoseconds",
            "offset",
        ],
        0.84,
    )

    # better match than bytes and bytearray or object
    candidates += simple_candidates("int", my_type, ["number of", "address of"], 0.95)
    # better match than bytes
    candidates += simple_candidates("bytearray", my_type, ["bytearray"], 0.83)

    # OK, better than just string
    candidates += simple_candidates("bytes", my_type, ["bytes", "byte string"], 0.81)

    candidates += simple_candidates("bool", my_type, ["boolean", "bool", "True", "False"], 0.8)
    candidates += simple_candidates(
        "float",
        my_type,
        ["float", "logarithm", "sine", "tangent", "exponential", "complex number", "phase"],
        0.8,
    )

    candidates += simple_candidates("str", my_type, ["string"], 0.8)

    candidates += simple_candidates("str", my_type, ["name", "names"], 0.3)
    ## TODO: "? contains 'None if there is no'  --> Union[Null, xxx]"
    candidates += simple_candidates(
        "None", my_type, ["``None``", "None"], 0.8, exclude=["previous value", "if there is no"]
    )

    candidates += object_candidates(my_type, 0.81)

    return candidates


def return_type_from_context(*, docstring: Union[str, List[str]], signature: str, module: str):
    try:
        return _type_from_context(module=module, signature=signature, docstring=docstring)["type"]
    except Exception:
        return "Any"


def _type_from_context(*, docstring: Union[str, List[str]], signature: str, module: str):
    """Determine the return type of a function or method based on:
     - the function signature
     - the terminology used in the docstring

    Logic:
      - if the signature contains a return type --> <something> then that is returned
        - use re to find phrases such as:
            - 'Returns ..... '
            - 'Gets  ..... '
            - 'Reads .....
        - docstring is joined without newlines to simplify parsing
        - then parses the docstring to find references to known types and give then a rating though a hand coded model ()
        - builds a list return type candidates
        - selects the highest ranking candidate
        - the default Type is 'Any'
    """

    if isinstance(docstring, list):
        # join with space to avoid ending at a newline
        docstring = " ".join(docstring)
    # regex match stops at end of sentence:: . ! ? : ;
    return_val_regex = r"Return value\s?:\s?(?P<return>[^.!?:;]*)"
    return_regex = r"Return(?:s?,?|(?:ing)?)\s(?!information)(?P<return>[^.!?:;]*)"
    gets_regex = r"Gets?\s(?P<return>[^.!?:;]*)"
    reads_regex = r"Read(?:s?,?)\s(?P<return>[^.!?:;]*)"

    # give the regex that searches for returns a 0.2 boost as that is bound to be more relevant
    weighted_regex = (
        (return_val_regex, 3),
        (return_regex, 1.8),
        (gets_regex, 1.5),
        (reads_regex, 1.0),
    )
    LIST_WEIGHT = 2.0
    # only the function name without the leading module
    function_re = re.compile(r"[\w|.]+(?=\()")

    matches: List[re.Match] = []
    candidates: List[Dict] = []

    # if the signature contains a return type , then use that and do nothing else.
    if "->" in signature:
        sig_type = signature.split("->")[-1].strip(": ")
        return {"type": sig_type, "confidence": LIST_WEIGHT, "match": signature}

    try:
        function_name = function_re.findall(signature)[0]
    except IndexError:
        function_name = signature.strip().strip(":()")

    function_name = ".".join((module, function_name))
    # lookup a few in the lookup list
    if function_name in LOOKUP_LIST.keys():
        sig_type = LOOKUP_LIST[function_name][0]
        return {
            "type": LOOKUP_LIST[function_name][0],
            "confidence": LOOKUP_LIST[function_name][1] * LIST_WEIGHT,
            "match": function_name,
        }
    for weighted in weighted_regex:

        match_iter = re.finditer(weighted[0], docstring, re.MULTILINE | re.IGNORECASE)
        for match in match_iter:
            # matches.append(match)
            distilled = distill_return(match.group("return"))
            for item in distilled:
                candidate = {
                    "match": match,
                    "type": item["type"],
                    "confidence": item["confidence"] * weighted[1],  # add search boost
                }
                candidates.append(candidate)
    # Sort
    # return the best candidate, or Any
    if len(candidates) > 0:
        candidates = sorted(candidates, key=lambda x: x["confidence"], reverse=True)
        log.info(candidates[0])
        return candidates[0]  # best candidate
    else:
        return {"type": "Any", "confidence": 0, "match": None}
