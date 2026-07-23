#!/usr/bin/env bash

# this script is referenced from the codespaces devcontainer dockerfile

echo "install uv before creating the venv" 
pipx install uv

#uv will create/refresh the project venv in .venv
echo "start: uv sync "
uv sync --group dev

echo "Activate virtual environment"
source .venv/bin/activate

# https://stackoverflow.com/questions/73485958/how-to-correct-git-reporting-detected-dubious-ownership-in-repository-withou
# git config --global safe.directory '*'

echo "run initial 'stubber clone'"
stubber clone --add-stubs
