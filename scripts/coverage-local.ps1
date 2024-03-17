# Install-Module -Name CredentialManagement
# Add-StoredCredentials  -UserName "codecov@micropython-stubber" -Password "e31c6aa7-0888-4666-aa9e-d486249b5c1e" 

$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri https://uploader.codecov.io/latest/windows/codecov.exe -Outfile codecov.exe

# run tests and create coverage reports
&coverage run -m pytest -m mpflash --junitxml=results/cov-mpflash.xml
&coverage run -m pytest -m stubber --junitxml=results/cov-stubber.xml

coverage lcov
coverage lcov  -o results/coverage.lcov
#coverage xml
# coverage json
coverage html 
start coverage\index.html

$env:CODECOV_TOKEN = (Get-ClearTextStoredCredentials  -Target "codecov@micropython-stubber").Password
.\codecov.exe -t ${env:CODECOV_TOKEN} -f results/cov-mpflash.xml -F mpflash
.\codecov.exe -t ${env:CODECOV_TOKEN} -f results/cov-stubber.xml -F stubber

# \develop\tools\codecov.exe -t ${env:CODECOV_TOKEN} results/cover*.xml
# \develop\tools\codecov.exe -t ${env:CODECOV_TOKEN} results/cover*.json


# for testspace just link to codecov
# \develop\tools\testspace.exe [dev]results/test-results*.xml --link codecov
