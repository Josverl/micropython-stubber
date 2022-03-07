# run tests and create coverage reports
coverage run -m pytest tests  --junitxml=results/test-results.xml
coverage xml
coverage json
coverage lcov
coverage html

start coverage\index.html

# Just a link to codecov
testspace tests-results.xml --link=codecov

\develop\tools\codecov.exe -t ${CODECOV_TOKEN} -s ./results
\develop\tools\testspace.exe [dev]results/test-results*.xml --link codecov
