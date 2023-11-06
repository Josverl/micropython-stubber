# Activate the venv

./.venv/bin/activate.ps1


#first update the stubs (local ) do not push updates
foreach ($version in @( "latest","v1.21.0", "v1.20.0", "v1.19.1" )) {
    stubber get-docstubs --version $version
    stubber get-frozen --version $version
    stubber merge --version $version --port auto --board auto
    stubber build --version $version --port auto --board auto
}
# then run the test with a clear cache to use the latest stubs
pytest -m 'snippets' --cache-clear