#!/usr/bin/env bash
# this script is referenced from the codespaces devcontainer dockerfile

echo "install poetry before creating the venv" 
pipx install poetry

#poetry will re-use the active venv or create a new one
echo "start: poetry install "
poetry install --with dev --sync

echo "Activate virtual environment"
source .venv/bin/activate

echo "run initial 'stubber clone'"
stubber clone --add-stubs
