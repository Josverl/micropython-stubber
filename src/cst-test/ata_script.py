# Ref: https://github.com/typeddjango/django-stubs/blob/99ed5b1a094bc441115a56fb01828b89e6906372/scripts/merge_stubs_into_django.py

from libcst import parse_module
from libcst.codemod import CodemodContext
from libcst.codemod.visitors import ApplyTypeAnnotationsVisitor

from pathlib import Path


def prRed(skk):
    print("\033[91m {}\033[00m".format(skk))


def prGreen(skk):
    print("\033[92m {}\033[00m".format(skk))


context = CodemodContext()
visitor = ApplyTypeAnnotationsVisitor(context)

# Stubs := Rich
# Sources: to be enriched

stubs_dir = "data/annotations/micropython-v1_16/"
sources_dir = "dev-stubs/micropython-esp32-1_15/"

stubs_dict = {}
sources_dict = {}

# list all the rich sources
stubs_pathlist = Path(stubs_dir).rglob("*.py")
for path in stubs_pathlist:
    # str_path = path.as_posix()
    rel_path = path.relative_to(stubs_dir)
    stubs_dict[rel_path.stem] = path.as_posix()

# now see what we can enrich with this
sources_pathlist = Path(sources_dir).rglob("*.py")
for path in sources_pathlist:
    rel_path = path.relative_to(sources_dir)
    if rel_path.stem in stubs_dict:
        sources_dict[rel_path.stem] = path.as_posix()

# then go to work
for key in stubs_dict:

    with open(stubs_dict[key]) as file:
        stub = file.read()

    stub_module = parse_module(stub)
    visitor.store_stub_in_context(context, stub_module)

    try:
        with open(sources_dict[key]) as file:
            source = file.read()
    except:
        prRed("No corresponding file for stub: " + stubs_dict[key])
        continue

    source_module = parse_module(source)
    result = visitor.transform_module(source_module)

    try:
        file = open(sources_dict[key], "w")
        file.write(result.code)
        file.close()
        prGreen(sources_dict[key])
    except:
        prRed("Error saving file: " + sources_dict[key])
