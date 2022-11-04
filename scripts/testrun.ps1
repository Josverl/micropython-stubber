
python -m libcst.tool codemod --include-stubs --no-format add_comment.AddComment .\repos\micropython-stubs\stubs\cpython_core-pycopy\ --comment "# CPython core - pycopy"
python -m libcst.tool codemod --include-stubs --no-format add_comment.AddComment .\repos\micropython-stubs\stubs\cpython_core-micropython\ --comment "# CPython core - micropython"

black .\repos\micropython-stubs\stubs\cpython_core-micropython\
black .\repos\micropython-stubs\stubs\cpython_core-pycopy\


$version = "v1.19.1"
# stubber switch $version
stubber -v get-docstubs

# stubber get-frozen 
python -m libcst.tool codemod --include-stubs --no-format  add_comment.AddComment .\repos\micropython-stubs\stubs\micropython-v1_19_1-frozen\ --comment "# Micropython 1.19.1 frozen stubs"
black .\repos\micropython-stubs\stubs\micropython-v1_19_1-frozen\
stubber merge --version $version

stubber publish --test-pypi --version $version --port auto --dry-run 
stubber publish --test-pypi --version $version --port esp32 --board um_tinypico --dry-run
# stubber publish --test-pypi --version $version --dry-run 



# foreach ($port in @("esp32", "esp8266", "stm32", "rp2")) {
    #     $stub_dir = ".\repos\micropython-stubs\publish\micropython-v1_19_1-$port-stubs"
    #     pip install -U $stub_dir --target typings\$port --no-user 
    #     # ignore asyncio for now
    #     del .\typings\$port\uasyncio -r
    # }
    # pyright .\typings_test\$port
    
$port = "stm32"
del .\typings\ -r
del .\typings2\ -r
$stub_dir = ".\repos\micropython-stubs\publish\micropython-v1_19_1-$port-stubs"
pip install -U $stub_dir --target typings --no-user 
# del .\typings\uasyncio -r
pyright .\typings