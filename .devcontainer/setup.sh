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

#poetry will re-use the active venv or create a new one
/home/vscode/.local/bin/poetry install

#Activate virtual environment
source .venv/bin/activate
