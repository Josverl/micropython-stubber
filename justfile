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