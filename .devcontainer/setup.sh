#!/bin/bash
# initialize the submodules
git submodule init
git submodule update

# initialize the python requirements
pip3 install --user -r requirements-dev.txt