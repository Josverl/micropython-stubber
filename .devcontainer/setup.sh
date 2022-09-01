#!/usr/bin/env bash
# this script is referenced from the codespaces devcontainer dockerfile


echo "install poetry before creating the venv" 
curl -sSL https://install.python-poetry.org | python3 - -y

#poetry will re-use the active venv or create a new one
echo "start: poetry install "
/home/vscode/.local/bin/poetry install

echo "Activate virtual environment"
source .venv/bin/activate

echo "run initial 'stubber clone'"
stubber clone 
