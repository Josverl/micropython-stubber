""" Work in Progress  

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

from . import utils

def process(folder: Path, pattern: str):
    # read all .json files in the folder
    report = []
    for file in folder.glob(pattern):
        if file.name == "report.json":
            continue  # just skip the report to avoid errors
        with open(file, errors="ignore", encoding="utf8") as fp:
            # read docstrings from json ( unsafe , assumes much )
            module_name = file.stem
            docstrings: List[Tuple] = json.load(fp)
            for item in docstrings:
                # module, class, function/method , line, docstring
                if item[4] != []:

                    signature = str(item[3]).split("::")[-1].strip()
                    docstring = item[4]

                    r = utils._type_from_context(
                        docstring=docstring, signature=signature, module=module_name
                    )
                    report.append(
                        {
                            "signature": signature,
                            "docstring": docstring,
                            "docstring_len": len(" ".join(docstring).strip()),
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
