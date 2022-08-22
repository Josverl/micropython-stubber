pydeps src/stubber --reverse --rankdir RL --cluster --max-cluster-size=10 --rmprefix stubber. --max-bacon=2  -o .\docs\img\dependencies.svg   
# External Deps hiding the internals 
pydeps src/stubber --reverse --rankdir RL --cluster --max-cluster-size=10 --collapse-target-cluster  -o .\docs\img\external_dependencies.svg 