# run tests and create coverage reports
coverage run -m pytest tests  --junitxml=results/test-results.xml
coverage xml
coverage json
coverage lcov
coverage html
start coverage\index.html