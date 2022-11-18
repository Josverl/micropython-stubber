
$version = "v1.19.1"
# stubber switch $version

stubber get-docstubs
stubber merge --version $version
stubber publish --test-pypi --version $version --port auto --board um_tinypico --dry-run

$ports = @("esp32", "esp8266", "stm32", "rp2")
# $ports = @("esp32")
$results = @()
foreach ($port in $ports) {
    $stub_source = ".\repos\micropython-stubs\publish\micropython-v1_19_1-$port-stubs"

    
    # port specifics
    $snippets_dir = ".\snippets\$port"
    $typings_dir = "$snippets_dir\typings"
    rd $typings_dir -r  -ea silentlycontinue
    pip install -U $stub_source --target $typings_dir --no-user 
    $result = pyright --project $snippets_dir --outputjson | convertfrom-json 
    $results += $result
    $result.generalDiagnostics | select severity, message, rule, file | ft  -AutoSize | out-host

    $snippets_dir = ".\snippets\common"
    $typings_dir = "$snippets_dir\typings"
    rd $typings_dir -r  -ea silentlycontinue
    pip install -U $stub_source --target $typings_dir --no-user 
    $result = pyright --project $snippets_dir --outputjson | convertfrom-json 
    $results += $result
    $result.generalDiagnostics | select severity, message, rule, file | ft  -AutoSize | out-host
}






$results | select -expand generalDiagnostics | ? { $_.severity -eq "error" } | out-host
$results | select summary | ft -auto



# 78 errors, 1 warning, 2 informations
# 72 errors, 1 warning, 2 informations
# 54 errors, 1 warning, 2 informations
# 1 error, 1 warning, 0 informations

# @{filesAnalyzed=124; errorCount=1; warningCount=1; informationCount=0; timeInSec=1,682}
# @{filesAnalyzed=121; errorCount=8; warningCount=6; informationCount=0; timeInSec=1,57}
# @{filesAnalyzed=100; errorCount=19; warningCount=5; informationCount=0; timeInSec=1,504}
# @{filesAnalyzed=121; errorCount=32; warningCount=3; informationCount=0; timeInSec=1,458}

# summary
# -------
# @{filesAnalyzed=118; errorCount=0; warningCount=0; informationCount=0; timeInSec=1,528}
# @{filesAnalyzed=131; errorCount=0; warningCount=0; informationCount=0; timeInSec=1,877}
# @{filesAnalyzed=114; errorCount=0; warningCount=5; informationCount=0; timeInSec=1,63}
# @{filesAnalyzed=128; errorCount=0; warningCount=5; informationCount=0; timeInSec=1,879}
# @{filesAnalyzed=93; errorCount=0; warningCount=8; informationCount=0; timeInSec=1,814}
# @{filesAnalyzed=108; errorCount=0; warningCount=8; informationCount=0; timeInSec=3,82}
# @{filesAnalyzed=112; errorCount=0; warningCount=3; informationCount=0; timeInSec=1,846}
# @{filesAnalyzed=123; errorCount=0; warningCount=3; informationCount=0; timeInSec=2,459}