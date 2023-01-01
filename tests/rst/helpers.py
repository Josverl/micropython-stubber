# others
from typing import List, Union

# SOT
from stubber.stubs_from_docs import RSTReader

###################################################################################################
# Helpers
####################################################################################################


def read_stub(folder, stubname):
    "Read the content of a generated stub"
    content: List[str] = []
    fl = list(folder.rglob(stubname))
    if len(fl):
        if file := fl[0]:
            with open(file) as f:
                content = f.readlines()
    return content


###################################################################################################
# Helpers
####################################################################################################


def load_rst(r: RSTReader, text: Union[str, List[str]]):
    "load a string or list of strings"
    r.rst_text = text if isinstance(text, List) else text.splitlines()
    r.max_line = len(r.rst_text)
    r.filename = "testmodule"
