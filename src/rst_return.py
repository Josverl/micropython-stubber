""" Work in Progress  
Tries to determine the return type by parsing the docstring and the function signature
 - if the signature contains a return type --> <something> then that is returned
 - use re to find phrases such as:
    - 'Returns ..... '
    - 'Gets  ..... '
 - docstring is joined without newlines to simplify parsing
 - then parses the docstring to find references to known types and give then a rating though a hand coded model ()
 - builds a list return type candidates 
 - selects the highest ranking candidate 
 - the default Type is 'Any'
 

todo: 

    - filter out obvious wrong types ( deny-list) 
    - regex :
        - 'With no arguments the frequency in Hz is returned.'
        - 'Get or set' --> indicates overloaded/optional return Union[None|...]
        - add regex for 'Query' ` Otherwise, query current state if no argument is provided. `

    - build test and  % report 
    - try if an Azure Machine Learning works as well 
        https://docs.microsoft.com/en-us/azure/machine-learning/quickstart-create-resources
    - 
"""
# ref: https://regex101.com/codegen?language=python
# https://regex101.com/r/D5ddB2/1


import json
from pathlib import Path
import re
from typing import Dict, List, Tuple, Union
import rst_utils as rst


def process(folder: Path, pattern: str):
    # read all .json files in the folder
    report = []
    for file in folder.glob(pattern):
        if file.name == "report.json":
            continue  # just skip the report to avoid errors
        with open(file, errors="ignore", encoding="utf8") as fp:
            # read docstrings from json ( unsafe , assumes much )
            docstrings: List[Tuple] = json.load(fp)
            for item in docstrings:
                # module, class, function/method , line, docstring
                if item[4] != []:
                    signature = str(item[3]).split("::")[-1].strip()
                    docstring = item[4]
                    r = rst.type_from_docstring(docstring, signature)
                    report.append(
                        {
                            "signature": signature,
                            "docstring": docstring,
                            "type": r["type"],
                            "confidence": r["confidence"],
                            "match": str(r["match"]),
                            "module": item[0],
                            "class": item[1],
                            "function/method": item[2],
                        }
                    )
                    isGood = r["confidence"] >= 0.5 and r["confidence"] <= 0.8 and item[2] != ""
                    isBad = r["confidence"] <= 0.5 and r["confidence"] <= 0.8 and item[2] != ""
                    if isBad:
                        context = item[3] + ".".join((item[0], item[1], item[2]))
                        try:
                            print(
                                f"{context:40} {r['type']:<15} - {r['confidence']} {r['match'].groups('return')}"
                            )
                        except:
                            print(f"{context:40} {r['type']:<15} - {r['confidence']} ")

                        # print(r)
    if len(report) > 0:
        filename = folder / "report.json"
        with open(filename, mode="w", encoding="utf8") as fp:
            json.dump(report, fp, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    process(Path("generated/micropython/1_16-nightly"), "*.json")
    # sample_authentication_with_api_key_credential()
