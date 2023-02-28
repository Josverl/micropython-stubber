# Install-Module -Name CredentialManagement
# Add-StoredCredentials  -UserName "codecov@micropython-stubber" -Password "87b31e69-0deb-4932-aed1-6d7ce81ceaa3" 

$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri https://uploader.codecov.io/latest/windows/codecov.exe -Outfile codecov.exe

# run tests and create coverage reports
coverage run -m pytest tests  --junitxml=results/test-results.xml

coverage lcov
coverage lcov  -o results/coverage.lcov
#coverage xml
# coverage json
coverage html

start coverage\index.html

$env:CODECOV_TOKEN = (Get-ClearTextStoredCredentials  -Target "codecov@micropython-stubber").Password
\develop\tools\codecov.exe -t ${env:CODECOV_TOKEN} -f results/cover*.lcov

# \develop\tools\codecov.exe -t ${env:CODECOV_TOKEN} results/cover*.xml
# \develop\tools\codecov.exe -t ${env:CODECOV_TOKEN} results/cover*.json


# for testspace just link to codecov
# \develop\tools\testspace.exe [dev]results/test-results*.xml --link codecov
