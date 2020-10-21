"just create typeshed stubs"
import utils
from utils import STUB_FOLDER

# now generate typeshed files for all scripts
print("Generate type hint files (pyi) in folder: {}".format(STUB_FOLDER))
utils.make_stub_files(STUB_FOLDER, levels=7)
