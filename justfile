# https://just.systems

# Set shell for Windows OSs:
set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

default:
    @just --list

# init the development environment
init:
    poetry install --with dev,test

# Build the project documentation
docs:
    @echo "Building documentation..."
    poetry install --with docs
    docs\make.bat html

# bump to the next patch level, including all .mpy files
next_patch:
    poetry version patch
    @just variants
    poetry version

variants:
    @echo "Building .mpy files..."
    stubber make-variants
    stubber make-variants --target ./mip/v5 --version 1.18
    stubber make-variants --target ./mip/v6 --version 1.19.1

build:
    @echo "Building the project..."
    poetry build

publish:
    @echo "Publishing the project..."
    @just build
    poetry publish

# build standalone ports
sa_build v="stable":
    uv run sa_ports_build.py --version {{v}} unix
    uv run sa_ports_build.py --version {{v}} windows

# stub standalone ports
sa_stub v="stable" p="unix":
    uv run sa_ports_stub.py --version {{v}} {{p}}


# Prepare for wasm (manual stub) 
[working-directory: 'webassembly-stubber']
wasm_stub:
    # make a temp folder
    mkdir -p WASM-TEMP
    echo "*" > WASM-TEMP/.gitignore
    # start webserver and browser
    uv run serve.py

# TODO
# Build stable and preview wasm binaries, using the 'pyscript'
wasm_build v="stable":
    # in all .pyi files
    # re.replace <JsProxy \d+> with <JsProxy nn>
    # re.replace -preview with ""
    # re.replace -233 with ""
    # re.replace 233 with ""
    # copy from temp folder to micropython-stubs/stubs 
    stubber merge --port webassembly --variant pyscript --version {{v}}
    stubber build --port webassembly --variant pyscript --version {{v}}
    
# wasm_build:
#     # uv run sa_ports_build.py --version stable webassembly --variant pyscript --fw-path webassembly-stubber/firmware/webassembly
#     uv run sa_ports_build.py --version preview webassembly --variant pyscript --fw-path webassembly-stubber/firmware/webassembly