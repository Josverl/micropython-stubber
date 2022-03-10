# Install-Module -Name CredentialManagement
# Add-StoredCredentials  -UserName "codecov@micropython-stubber" -Password "123" 

# run tests and create coverage reports
coverage run -m pytest tests  --junitxml=results/test-results.xml

coverage lcov
#coverage xml
# coverage json
coverage html

start coverage\index.html


$env:CODECOV_TOKEN = (Get-ClearTextStoredCredentials  -Target "codecov@micropython-stubber").Password
\develop\tools\codecov.exe -t ${env:CODECOV_TOKEN} ./results/cover*.lcov
# \develop\tools\codecov.exe -t ${env:CODECOV_TOKEN} ./results/cover*.xml
# \develop\tools\codecov.exe -t ${env:CODECOV_TOKEN} ./results/cover*.json


# for testspace just link to codecov
\develop\tools\testspace.exe [dev]results/test-results*.xml --link codecov
