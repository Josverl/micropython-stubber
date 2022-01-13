# run pylint and pyright in order to updload results to testspace
# requires testspace config to be present & configured 

pylint --output-format=parseable ./board --ignore-paths=board/stubs  > pylint-checks.log
pyright > pyright-checks.log
pyright all-stubs > pyright-all-stubs.log

# regex repl: 
#     ' - (info|warning|error):'
foreach ( $file in @('pyright-all-stubs.log', 'pyright-checks.log')) {
    (Get-Content $file) `
        -replace ' - (info|warning|error):', ': $1:' | `
        Out-File $file
}

# \develop\tools\testspace ".\pyright-checks.log{lint}"
\develop\tools\testspace [all-stubs]".\pyright-all-stubs.log{lint}" [pyright]".\pyright-checks.log{lint}" [pylint]".\pylint-checks.log{lint}"