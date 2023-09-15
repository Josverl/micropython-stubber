param(
    $version = "latest",
    [string[]]$ports = @("esp32", "esp8266", "stm32", "rp2", "samd"),
    [switch]$do_docstubs = $False,
    [switch]$do_merge = $False,
    [switch]$do_build = $False
)

$flatversion = $version.replace(".", "_")
#Cascade the build steps
if ($do_docstubs) {
    $do_merge = $True
}
if ($do_merge) {
    $do_build = $True
}

$snippetsroot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workplaceroot = Split-Path -Parent ($snippetsroot)

$prior_cwd = Get-Location
cd $workplaceroot

echo "--------------------------------------------------------"
echo "version: $version"
echo "flatversion: $flatversion"
echo "ports: $ports"

if ($do_docstubs) {
    echo "--------------------------------------------------------"
    echo "get-docstubs $version"
    echo "--------------------------------------------------------"
    stubber switch $version
    stubber get-docstubs
    # update micropython-core from recent docstubs
    stubber enrich -s $workplaceroot\repos\micropython-stubs\stubs\micropython-core -ds $workplaceroot\repos\micropython-stubs\stubs\micropython-$flatversion-docstubs
}


if ($do_merge ) {
    echo "--------------------------------------------------------"
    echo "merge $version"
    echo "--------------------------------------------------------"
    foreach ($port in $ports) {
        stubber merge --version $version --port $port
    }
}

if ($do_build) {
    echo "--------------------------------------------------------"
    echo "build"
    echo "--------------------------------------------------------"

    foreach ($port in $ports) {
        stubber build --version $version --port $port
    }
    # stubber build --version $version --port rp2 --board pico_w 
    # stubber publish --test-pypi --version $version --port auto --board um_tinypico --dry-run
}


# first install the typestubs to a local folder so they can be copied from there to save time

foreach ($port in $ports) {

    $stub_source = "$workplaceroot\repos\micropython-stubs\publish\micropython-$flatversion-$port-stubs"
    $typings_cache_dir = "$workplaceroot\snippets\typings_$port"
    echo "--------------------------------------------------------"
    echo "port: $port"
    echo "type cache : $typings_cache_dir"
    echo "--------------------------------------------------------"

    rd $typings_cache_dir -r -ea silentlycontinue
    # pip install including pre-releases to get the latest stdlib version
    pip install  -I $stub_source --target $typings_cache_dir --no-user --pre
}

# create a hashtable with feates as a key, and the orts that support it as a lisy
$features = @{
    "networking" = @("esp32", "esp8266", "rp2-pico-w")
    "bluetooth"  = @("esp32")
}

$results = @()
foreach ($port in $ports) {
    $stub_source = "$workplaceroot\repos\micropython-stubs\publish\micropython-$flatversion-$port-stubs"
    $typings_cache_dir = "$workplaceroot\snippets\typings_$port"

    if (-not (Test-Path $typings_cache_dir)) {
        Write-Warning "The directory '$typings_cache_dir' does not exist."
        continue
    }

    foreach ($folder  in @($port, "stdlib", "micropython", "networking", "bluetooth")) {
        if ($features.Contains($folder)) {
            if ($port -notin $features[$folder]) {
                # do not check features on ports that do not support it
                # TODO: add boards such as the rp2 pico-W that do support it
                continue
            }
        }
        if ($folder.startswith($port)) {
            $snippets_dir = "$workplaceroot\snippets\check_$folder"
        }
        else {
            $snippets_dir = "$workplaceroot\snippets\feat_$folder"
        }
        $typings_dir = "$snippets_dir\typings"
        echo "--------------------------------------------------------"
        echo "port: $port "
        echo "folder: $folder"
        echo "snippets_dir: $snippets_dir"
        echo "--------------------------------------------------------"
        if (-not (test-path $snippets_dir)) {
            Write-Warning "The directory '$snippets_dir' does not exist."
            continue
        }
        
        
        rd $typings_dir -r  -ea silentlycontinue
        # copy typings from the cache to the snippets folder
        Copy-Item $typings_cache_dir $typings_dir -Recurse -Force
        
        # run pyright
        $result = pyright --project $snippets_dir --outputjson | convertfrom-json 
        # add $port attribute  to result
        Add-Member -InputObject $result.summary -MemberType NoteProperty -Name port -Value $port
        Add-Member -InputObject $result.summary -MemberType NoteProperty -Name folder -Value $folder
        
        foreach ($diag in $result.generalDiagnostics) {
            add-member -InputObject $diag -MemberType NoteProperty -Name port -Value $port
            add-member -InputObject $diag -MemberType NoteProperty -Name folder -Value $folder
        }        
        $results += $result
        $result.generalDiagnostics | select port, folder, severity, rule, file, message | ft -Wrap | out-host 
    }
}
# resore working directory
cd $prior_cwd

echo "========================================================"

$results | select -expand generalDiagnostics | ? { $_.severity -eq "error" } | select port, folder, severity, rule, file, message | ft -Wrap | out-host
echo "========================================================"

# Write results to file
$results | select -expand generalDiagnostics | ? { $_.severity -eq "error" } | Export-Csv -Path $snippetsroot\results.csv -NoTypeInformation 
# And to .json
$results | ConvertTo-Json -Depth 10 | Out-File $snippetsroot\results.json -Force
