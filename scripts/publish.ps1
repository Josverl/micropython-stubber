
# poetry config pypi-token.test-pypi <token-1>
# poetry config pypi-token.pypi <token-2>

poetry version prerelease
poetry build
poetry publish -r test-pypi 

