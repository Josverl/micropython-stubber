# Install-Module -Name CredentialManagement
# Add-StoredCredentials  -UserName "codecov@micropython-stubber" -Password "e31c6aa7-0888-4666-aa9e-d486249b5c1e" 

$ProgressPreference = 'SilentlyContinue'
# Invoke-WebRequest -Uri https://uploader.codecov.io/latest/windows/codecov.exe -Outfile codecov.exe
pip install -U codecov-cli

# run tests and create coverage reports
$env:CODECOV_TOKEN = (Get-ClearTextStoredCredentials  -Target "codecov@micropython-stubber").Password

coverage erase

coverage run -m pytest -m mpflash
coverage xml -o results/coverage-mpflash.xml
coverage lcov -o results/coverage.lcov
coverage html 
start coverage\index.html

coverage run -m pytest -m stubber
coverage xml -o results/coverage-all.xml
coverage lcov -o results/coverage.lcov
coverage html 
start coverage\index.html

codecov -t ${env:CODECOV_TOKEN} -f coverage-all.xml




# for testspace just link to codecov
# \develop\tools\testspace.exe [dev]results/test-results*.xml --link codecov
