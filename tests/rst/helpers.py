# others
from typing import List, Union

# SOT
from stubber.rst.reader import RSTWriter

###################################################################################################
# Helpers
####################################################################################################


def read_stub(folder, stubname):
    "Read the content of a generated stub"
    content: List[str] = []
    fl = list(folder.rglob(stubname))
    if len(fl):
        file = fl[0]
        if file:
            with open(file) as f:
                content = f.readlines()
    return content


###################################################################################################
# Helpers
####################################################################################################


def load_rst(r: RSTWriter, text: Union[str, List[str]]):
    "load a string or list of strings"
    if isinstance(text, List):
        r.rst_text = text
    else:
        r.rst_text = text.splitlines()
    r.max_line = len(r.rst_text)
    r.filename = "testmodule"
