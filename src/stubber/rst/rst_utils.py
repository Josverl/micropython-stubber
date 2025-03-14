"""
Work in Progress
----------------

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
 

to do:

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

import re
from typing import Dict, List, Optional, Union

from mpflash.logger import log

from .lookup import LOOKUP_LIST, NONE_VERBS, TYPING_IMPORT

# These are shown to import
__all__ = [
    "simple_candidates",
    "compound_candidates",
    "object_candidates",
    "distill_return",
    "return_type_from_context",
    "_type_from_context",  # For testing only
    "TYPING_IMPORT",
]


# logging
# # log = logging.getLogger(__name__)


# --------------------------------------
# Confidence levels
# these heuristics are based a significant amout of manual testing,
# and not based on any statistical analysis

C_DEFAULT = 0  # Any , the default for all
C_NONE = 0.1 + C_DEFAULT  # better than the default Any
C_BASE = 0.1 + C_NONE  # the Base if a return type has been found

C_STR_NAMES = 0.3

C_GENERIC = 0.6
C_DICT = C_GENERIC
C_TUPLE = C_GENERIC
C_LIST = C_GENERIC
C_BOOL = C_GENERIC
C_FLOAT = C_GENERIC
C_STR = C_GENERIC

# tehere is a bit of logic - but mostly empirical
C_NONE_RETURN = C_GENERIC
C_OBJECTS = 0.01 + C_GENERIC

C_BYTES = 0.01 + C_GENERIC
C_BYTEARRAY = 0.03 + C_GENERIC
C_INT = 0.03 + C_GENERIC
C_UINT = 0.04 + C_GENERIC
C_ITERATOR = 0.4 + C_GENERIC
C_GENERATOR = 0.4 + C_GENERIC

C_INT_SIZES = 0.5 + C_GENERIC  # better match than bytes and bytearray or object
C_INT_LIKE = 0.5 + C_GENERIC

C_LOOKUP = C_GENERIC + 1

# --------------------------------------
# Weights of the different Lookups
WEIGHT_LOOPUPS = 3.0  # Lookup list weight factor
WEIGHT_RETURN_VAL = 3.0  # Lookup list weight factor
WEIGHT_RETURNS = 1.8  # for Docstring returns
WEIGHT_GETS = 1.5  # For docstring Gets

# --------------------------------------

# base has a confidence that is quite low, but better than rubbish
BASE = {"type": "Incomplete", "confidence": C_BASE, "match": None}

# --------------------------------------
# Regexes
# --------------------------------------

# all regex matches stop at end of sentence:: . ! ? : ;
# Look for "Return Value: xxxx"
RE_RETURN_VALUE = r"Return value\s?:\s?(?P<return>[^.!?:;]*)"
# Look for Returns , but no 'Information'
RE_RETURN = r"Return(?:s?,?|(?:ing)?)\s(?!information)(?P<return>[^.!?:;]*)"
# Look for gets
RE_GETS = r"Gets?\s(?P<return>[^.!?:;]*)"

# --------------------------------------
# Regex for Literals
# --------------------------------------
RE_LIT_AS_A = r"as a\s?(?P<return>[^.!?:;]*)"
RE_LIT_SENTENCE = r"\s?(?P<return>[^.!?:;]*)"


def dist_rate(i: int) -> float:
    """"""
    max_len = 150  # must occur in the first 150 chars
    return max((max_len - i), 1) / max_len


WORD_TERMINATORS = ".,!;:?"


def simple_candidates(
    type: str,
    match_string: str,
    keywords: List[str],
    rate: float = 0.5,
    exclude: Optional[List[str]] = None,
):
    """
    find and rate possible types and confidence weighting for simple types.
    Case sensitive
    """
    if exclude is None:
        exclude = []
    candidates = []
    if not any(t in match_string for t in keywords) or any(t in match_string for t in exclude):
        # quick bailout , there are no matches, or there is an exclude
        return []

    #  word matching
    match_words = [w.strip(WORD_TERMINATORS) for w in match_string.split()]
    #  kw =  single word -
    for kw in keywords:
        i = match_string.find(kw)
        if " " not in kw and kw not in match_words or " " in kw and i < 0:
            continue
        # Assume unsigned are int
        result = BASE.copy()
        result["type"] = type
        result["confidence"] = rate * dist_rate(i)  # OK
        log.trace(f" - found '{kw}' at position {i} with rating {dist_rate(i)}")
        candidates.append(result)
    return candidates


def compound_candidates(
    type: str,
    match_string: str,
    keywords: List[str],
    rate: float = 0.85,
    exclude: Optional[List[str]] = None,
):
    """
    find and rate possible types and confidence weighting for compound types that can have a subscription.
    Case sensitive
    """
    if exclude is None:
        exclude = []
    candidates = []
    if not any(t in match_string for t in keywords) or any(t in match_string for t in exclude):
        # quick bailout , there are no matches, or there is an exclude
        return []

    #  word matching
    match_words = [w.strip(WORD_TERMINATORS) for w in match_string.split()]
    #  kw =  single word -
    for kw in keywords:
        i = match_string.find(kw)
        if " " not in kw and kw not in match_words or " " in kw and i < 0:
            continue
        # List / Dict / Generator of Any / Tuple /
        sub = None
        result = BASE.copy()
        confidence = rate
        for element in ("tuple", "string", "unsigned", "int"):
            if element in match_string.casefold():
                j = match_string.find(element)
                if i == j:
                    # do not match on the same main and sub
                    continue
                confidence += 0.10  # boost as we have a subtype
                if element == "string":
                    sub = "str"
                    break
                elif element == "tuple":
                    sub = "Tuple"
                    break
                elif element == "unsigned":
                    sub = "int"
                    break
                else:
                    sub = element
        result["type"] = f"{type}[{sub}]" if sub else f"{type}"
        confidence = confidence * dist_rate(i)  # distance weighting
        result["confidence"] = confidence
        log.trace(
            f" - found '{kw}' at position {i} with confidence {confidence} rating {dist_rate(i)}"
        )

        candidates.append(result)
    return candidates


def object_candidates(match_string: str, rate: float = 0.81, exclude: Optional[List[str]] = None):
    """
    find and rate possible types and confidence weighting for Object types.
    Case sensitive
    Exclude defaults to ["IRQ"]
    """
    # defaults
    if exclude is None:
        exclude = ["IRQ"]
    candidates = []
    keywords = [
        "Object",
        "object",
    ]  # Q&D

    if not any(t in match_string for t in keywords) or any(t in match_string for t in exclude):
        # quick bailout , there are no matches, or there is an exclude
        return []
    for kw in keywords:
        i = match_string.find(kw)
        if i < 0:
            continue
        # List / Dict / Generator of Any / Tuple /
        confidence = rate

        # did the word actually occur, or is it just a partial
        words = match_string.split(" ")  # Return <multiple words object>
        if kw in words:
            pos = words.index(kw)
            obj = "Incomplete" if pos == 0 else words[pos - 1]
            if obj in ("stream-like", "file"):
                obj = "IO"  # needs from typing import IO
            elif obj == "callback":
                obj = "Callable[..., Incomplete]"  # requires additional 'from typing import Callable'
            else:
                # clean
                obj = re.sub(r"[^a-z.A-Z0-9]", "", obj)
            result = BASE.copy()
            result["type"] = obj
            if obj in ["an", "any"]:  # "Return an / any object"
                result["type"] = "Incomplete"
                confidence += 0.10  # abstract , but very good
            elif obj[0].islower():
                confidence -= 0.20  # not so good
            result["confidence"] = confidence * dist_rate(i)
            candidates.append(result)
    return candidates


def has_none_verb(docstr: str) -> List:
    "returns a None result if the docstring starts with a verb that indicates None"
    docstr = docstr.strip().casefold()
    if not any(docstr.startswith(kw.casefold()) for kw in NONE_VERBS):
        return []
    result = BASE.copy()
    result["type"] = "None"
    result["confidence"] = C_NONE  # better than the default Any
    return [result]


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

    # clean up match_string
    match_string = return_text.strip().rstrip(".")
    match_string = match_string.replace("`", "")

    candidates += compound_candidates("Generator", match_string, ["generator"], C_GENERATOR)
    candidates += compound_candidates("Iterator", match_string, ["iterator"], C_ITERATOR)
    candidates += compound_candidates(
        "List", match_string, ["a list of", "list of", "an array"], C_LIST
    )

    candidates += simple_candidates(
        "Dict", match_string, ["a dictionary", "dict", "Dictionary"], C_DICT
    )
    candidates += simple_candidates(
        "Tuple",
        match_string,
        [
            "tuple",
            "a tuple",
            "a pair",
            "1-tuple",
            "2-tuple",
            "3-tuple",
            "4-tuple",
            "5-tuple",
            "6-tuple",
            "7-tuple",
            "8-tuple",
            "9-tuple",
        ],
        C_TUPLE,
    )

    candidates += simple_candidates(
        "int", match_string, ["unsigned integer", "unsigned int", "unsigned"], C_UINT
    )

    candidates += simple_candidates(
        "int",
        match_string,
        [
            "number",
            "integer",
            "count",
            "int",
            "0 or 1",
        ],
        C_INT,
    )

    # good but nor perfect indicators of integers
    # better match than bytes and bytearray or object
    candidates += simple_candidates(
        "int",
        match_string,
        [
            "length",
            "total size",
            "size of",
            "the index",
            "number of",
            "address of",
            "the duration",
        ],
        C_INT_SIZES,
    )

    candidates += simple_candidates("int", match_string, [], C_INT_SIZES)

    # Assume numbers are signed int
    candidates += simple_candidates(
        "int",
        match_string,
        [
            "index",
            "**signed** value",
            "seconds",
            "nanoseconds",
            "millisecond",
            "offset",
        ],
        C_INT_LIKE,
    )

    # better match than bytes
    candidates += simple_candidates("bytearray", match_string, ["bytearray"], C_BYTEARRAY)

    # OK, better than just string
    candidates += simple_candidates("bytes", match_string, ["bytes", "byte string"], C_BYTES)

    candidates += simple_candidates(
        "bool", match_string, ["boolean", "bool", "True", "False"], C_BOOL
    )
    candidates += simple_candidates(
        "float",
        match_string,
        [
            "float",
            "logarithm",
            "sine",
            "cosine",
            "tangent",
            "exponential",
            "complex number",
            "phase",
            "ratio of",
        ],
        C_FLOAT,
    )

    candidates += simple_candidates(
        "str", match_string, ["string", "(sub)string", "sub-string", "substring"], C_STR
    )

    candidates += simple_candidates("str", match_string, ["name", "names"], C_STR_NAMES)
    ## "? contains 'None if there is no'  --> Union[Null, xxx]"
    candidates += simple_candidates(
        "None",
        match_string,
        ["``None``", "None"],
        C_NONE_RETURN,
        exclude=["previous value", "if there is no"],
    )

    candidates += object_candidates(match_string, C_OBJECTS)

    return candidates


def return_type_from_context(
    *, docstring: Union[str, List[str]], signature: str, module: str, literal: bool = False
):
    try:
        return str(
            _type_from_context(
                module=module, signature=signature, docstring=docstring, literal=literal
            )["type"]
        )
    except Exception:
        return "Incomplete"


def _type_from_context(
    *, docstring: Union[str, List[str]], signature: str, module: str, literal: bool = False
):  # -> Dict[str , Union[str,float]]:
    """Determine the return type of a function or method based on:
     - the function signature
     - the terminology used in the docstring

    Logic:
    - if the signature contains a return type --> <something> then that is returned
    - use re to find phrases such as:

        - 'Returns ..... '
        - 'Gets  ..... '

    - docstring is joined without newlines to simplify parsing
    - then parses the docstring to find references to known types and give then a rating though a hand coded model ()
    - builds a list return type candidates
    - selects the highest ranking candidate
    - the default Type is 'Incomplete'
    """

    if isinstance(docstring, list):
        # join with space to avoid ending at a newline
        docstring = " ".join(docstring)

    # give the regex that searches for returns a 0.2 boost as that is bound to be more relevant

    weighted_regex = (
        [
            (RE_LIT_AS_A, 1.0),
            (RE_LIT_SENTENCE, 2.0),
        ]
        if literal
        else [
            (RE_RETURN_VALUE, WEIGHT_RETURN_VAL),
            (RE_RETURN, WEIGHT_RETURNS),
            (RE_GETS, WEIGHT_GETS),
            #       (reads_regex, 1.0),
        ]
    )
    # only the function name without the leading module
    function_re = re.compile(r"[\w|.]+(?=\()")

    # matches: List[re.Match] = []
    candidates: List[Dict] = [{"match": "default", "type": "Incomplete", "confidence": 0}]

    # if the signature contains a return type , then use that and do nothing else.
    if "->" in signature:
        sig_type = signature.split("->")[-1].strip(": ")
        return {"type": sig_type, "confidence": WEIGHT_LOOPUPS, "match": signature}

    # ------------------------------------------------------
    # lookup returns that cannot be found based on the docstring from the lookup list
    if "(" in signature:
        # method / function / class
        try:
            item_name = function_re.findall(signature)[0]
        except IndexError:
            item_name = signature.strip().strip(":()")
    else:
        # module or class attribute
        item_name = signature.replace(".. data::", "").strip()

    mod_last = module.split(".")[-1]
    item_first = item_name.split(".")[0]
    name_repeat = mod_last == item_first
    if name_repeat:
        # avoid machine.UART.UART.irq or pyb.pyb.hid_mouse
        item_name = f"{module}.{item_name}".replace(f"{mod_last}.{item_first}", mod_last)
    else:
        item_name = f"{module}.{item_name}"

    if item_name in LOOKUP_LIST.keys():
        sig_type = LOOKUP_LIST[item_name][0]
        return {
            "type": sig_type,
            "confidence": C_LOOKUP * WEIGHT_LOOPUPS,
            "match": item_name,
        }
    # ------------------------------------------------------
    # parse the docstring for simple start verbs,
    # and add them as a candidate
    candidates += has_none_verb(docstring)

    # ------------------------------------------------------
    # parse the docstring for the regexes and weigh the results accordingly
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
    candidates = sorted(candidates, key=lambda x: x["confidence"], reverse=True)
    best = candidates[0]  # best candidate

    # ref: https://docs.python.org/3/library/typing.html#typing.Coroutine
    # Coroutine[YieldType, SendType, ReturnType]
    # todo: sanity check against actual code .....
    if "This is a coroutine" in docstring and "Coroutine" not in str(best["type"]):  # type: ignore
        best["type"] = f"Coroutine[{best['type']}, Any, Any]"

    # return the best candidate, or Any
    return best  # best candidate
