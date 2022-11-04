

$version = "v1.19.1"
# stubber switch $version
# stubber -v get-docstubs
stubber merge --version $version
stubber publish --test-pypi --version $version --port auto --board um_tinypico --dry-run

$port = "esp32"
$results = @()
# foreach ($port in @("esp32")) {
foreach ($port in @("esp32", "esp8266", "stm32", "rp2")) {
    $stub_dir = ".\repos\micropython-stubs\publish\micropython-v1_19_1-$port-stubs"
    $snippets_dir = ".\snippets\$port"
    $typings_dir = "$snippets_dir\typings"
    
    rd $typings_dir -r 
    pip install -U $stub_dir --target $typings_dir --no-user 
    $result = pyright $snippets_dir --outputjson | convertfrom-json 
    $results += $result
    $result.generalDiagnostics | select severity, message, rule, file | ft  -AutoSize | out-host
}

$results | select -expand generalDiagnostics | out-host
$results | select summary | ft -auto

# foreach ($port in @("esp32", "esp8266", "stm32", "rp2")) {
#     $stub_dir = ".\repos\micropython-stubs\publish\micropython-v1_19_1-$port-stubs"
#     pip install -U $stub_dir --target typings\$port --no-user 
#     # ignore asyncio for now
#     del .\typings\$port\uasyncio -r
# }
# pyright .\typings_test\$port


# 78 errors, 1 warning, 2 informations
# 72 errors, 1 warning, 2 informations
# 54 errors, 1 warning, 2 informations
# 1 error, 1 warning, 0 informations

# @{filesAnalyzed=124; errorCount=1; warningCount=1; informationCount=0; timeInSec=1,682}
# @{filesAnalyzed=121; errorCount=8; warningCount=6; informationCount=0; timeInSec=1,57}
# @{filesAnalyzed=100; errorCount=19; warningCount=5; informationCount=0; timeInSec=1,504}
# @{filesAnalyzed=121; errorCount=32; warningCount=3; informationCount=0; timeInSec=1,458}

# @{filesAnalyzed=124; errorCount=1; warningCount=1; informationCount=0; timeInSec=2,02}
# @{filesAnalyzed=121; errorCount=2; warningCount=6; informationCount=0; timeInSec=1,648}
# @{filesAnalyzed=100; errorCount=14; warningCount=5; informationCount=0; timeInSec=1,466}
# @{filesAnalyzed=121; errorCount=9; warningCount=3; informationCount=0; timeInSec=1,808}

@{filesAnalyzed = 124; errorCount = 1; warningCount = 0; informationCount = 0; timeInSec = 1, 943 }
@{filesAnalyzed = 121; errorCount = 2; warningCount = 5; informationCount = 0; timeInSec = 2, 124 }
@{filesAnalyzed = 100; errorCount = 10; warningCount = 5; informationCount = 0; timeInSec = 2, 08 }
@{filesAnalyzed = 121; errorCount = 9; warningCount = 3; informationCount = 0; timeInSec = 2, 288 }