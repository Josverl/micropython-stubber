

$version = "v1.20.0"
$version = "latest"
$flatversion = $version -replace "\.", "_"

$ports = @("esp32")
$ports = @("esp32", "esp8266", "stm32", "rp2", "samd")
$ports = @("rp2")
$do_docstubs = $false
$do_merge = $True
$do_build = $true


echo "--------------------------------------------------------"
echo "version: $version"
echo "flatversion: $flatversion"
echo "ports: $ports"

if ($do_docstubs) {
    echo "--------------------------------------------------------"
    echo "docstubs"
    echo "--------------------------------------------------------"
    stubber switch $version
    stubber get-docstubs
}
if ($do_merge ) {
    echo "--------------------------------------------------------"
    echo "merge"
    echo "--------------------------------------------------------"
    foreach ($port in $ports) {
        stubber -v merge --version $version --port $port
    }
}
if ($do_build) {
    echo "--------------------------------------------------------"
    echo "build"
    echo "--------------------------------------------------------"

    foreach ($port in $ports) {
        stubber -v build --version $version --port $port
    }
    # stubber build --version $version --port rp2 --board pico_w 
    # stubber publish --test-pypi --version $version --port auto --board um_tinypico --dry-run
}



$results = @()
foreach ($port in $ports) {
    $stub_source = ".\repos\micropython-stubs\publish\micropython-$flatversion-$port-stubs"
    echo "--------------------------------------------------------"
    echo "port: $port"
    echo "stub_source: $stub_source"
    echo "--------------------------------------------------------"

    foreach ($snippets_dir in @(".\snippets\$port", ".\snippets\common", ".\snippets\stdlib")) {
        $typings_dir = "$snippets_dir\typings"
        rd $typings_dir -r  -ea silentlycontinue
        pip install -U $stub_source --target $typings_dir --no-user 
        $result = pyright --project $snippets_dir --outputjson | convertfrom-json 
        $results += $result
        $result.generalDiagnostics | select severity, message, rule, file | ft  -AutoSize | out-host
    }
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