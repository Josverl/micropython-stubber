#!/usr/bin/env bash
# this script is referenced from the codespaces devcontainer dockerfile

git submodule init
git submodule update

cd micropython
git remote add --tags micropython https://github.com/micropython/micropython.git
git fetch --all --tags
cd ..

#
if [ "${CODESPACES}" = "true" ]; then
    # create & activate venv and install the dependencies in there 
    python -m venv .venv-cs
    source .venv-cs/bin/activate
else
    python3 -m venv .venv-ub
    source .venv-ub/bin/activate
fi
# python -m pip install --upgrade pip
# python -m pip install -r requirements-dev.txt
pip install poetry
poetry install
