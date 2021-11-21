# Ref: https://github.com/typeddjango/django-stubs/blob/99ed5b1a094bc441115a56fb01828b89e6906372/scripts/merge_stubs_into_django.py


from libcst import parse_module, CSTValidationError, Module
from libcst.codemod import CodemodContext
from codemod.visitors import ApplyStubberAnnotationsVisitor

from pathlib import Path


def prRed(skk):
    print("\033[91m {}\033[00m".format(skk))


def prGreen(skk):
    print("\033[92m {}\033[00m".format(skk))


context = CodemodContext()
visitor = ApplyStubberAnnotationsVisitor(context)

# Stubs := Rich
# Sources: to be enriched

stubs_dir = "all-stubs/micropython-v1_16-documentation/"
sources_dir = "dev-stubs/micropython-v1_16-esp32/"

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
    except Exception:
        prRed("No corresponding file for stub: " + stubs_dict[key])
        continue
    source_module: Module
    try:
        source_module = parse_module(source)
        result = visitor.transform_module(source_module)
        # will throw errors on incorrect stub application / syntax
        # - Must have at least one kwonly param if ParamStar is used.
        # - Must have at least one posonly param if ParamSlash is used.
        #       def time_pulse_us(pin: Pin, pulse_level: int, timeout_us: int = 1000000, /) -> int:
        #       works when changed to :
        #       def time_pulse_us(__pin: Pin, pulse_level: int, timeout_us: int = 1000000, /) -> int:
        # so we'll need to check the manual typehints somehow for these type of notation mistakes

    except CSTValidationError as e:
        print(e)

    try:
        prGreen(sources_dict[key])
        print(result.code)
        prGreen(sources_dict[key])
        # file = open(sources_dict[key], "w")
        # file.write(result.code)
        # file.close()
    except Exception:
        prRed("Error saving file: " + sources_dict[key])

    # Also look at
    # https://github.com/sandnattanicha/Final-Project/blob/a45db843058f8b1844c146a35911a674eb8a01aa/dir-name/libcst/codemod/visitors/tests/test_apply_type_annotations.py

    # def tst_annotate_functions_with_existing_annotations(
    #     self, stub: str, before: str, after: str
    # ) -> None:
    #     context = CodemodContext()
    #     ApplyTypeAnnotationsVisitor.store_stub_in_context(
    #         context, parse_module(textwrap.dedent(stub.rstrip()))
    #     )
    #     # Test setting the overwrite flag on the codemod instance.
    #     self.assertCodemod(
    #         before, after, context_override=context, overwrite_existing_annotations=True
    #     )

    #     # Test setting the flag when storing the stub in the context.
    #     context = CodemodContext()
    #     ApplyTypeAnnotationsVisitor.store_stub_in_context(
    #         context,
    #         parse_module(textwrap.dedent(stub.rstrip())),
    #         overwrite_existing_annotations=True,
    #     )
    #     self.assertCodemod(before, after, context_override=context)
