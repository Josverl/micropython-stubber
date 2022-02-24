#!/usr/bin/env bash
# this script is referenced from the codespaces devcontainer dockerfile

git submodule init
git submodule update

cd micropython
git remote add --tags micropython https://github.com/micropython/micropython.git
git fetch --all --tags
cd ..
# install poetry before creating the venv
curl -sSL https://install.python-poetry.org | python3 - -y

#
if [ "${CODESPACES}" = "true" ]; then
    # create & activate venv and install the dependencies in there 
    python -m venv .venv
    source .venv/bin/activate
else
    python3 -m venv .venv-ub
    source .venv-ub/bin/activate
fi
#poetry will re-use the active venv
/home/vscode/.local/bin/poetry install
