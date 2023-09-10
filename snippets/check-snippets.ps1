# Used to check the snippets for errors
# Requires pyright to be installed

$snip_root = $PSScriptRoot 


$version = "v1.20.0"
$version = "latest"
$flatversion = $version -replace "\.", "_"

# , "samd"
$ports = @("esp32", "esp8266", "stm32", "rp2")

$results = @()
foreach ($port in $ports) {
    echo "--------------------------------------------------------"
    
    foreach ($snip_folder in @($port, "common", "stdlib")) {
        echo "--------------------------------------------------------"
        echo "port: $port snip_folder: $snip_folder"
        echo "--------------------------------------------------------"
        $snippets_dir = join-path $snip_root $snip_folder
        $result = pyright --project $snippets_dir --outputjson | convertfrom-json 
        # add $port attribute  to result
        Add-Member -InputObject $result.summary -MemberType NoteProperty -Name port -Value $port
        Add-Member -InputObject $result.summary -MemberType NoteProperty -Name snip_folder -Value $snip_folder

        foreach ($diag in $result.generalDiagnostics) {
            add-member -InputObject $diag -MemberType NoteProperty -Name port -Value $port
            add-member -InputObject $diag -MemberType NoteProperty -Name snip_folder -Value $snip_folder
        }


        $results += $result
        $result.generalDiagnostics | select severity, message, rule, file | ft  -AutoSize | out-host
    }
}

# Save results to json
$results | convertto-json | out-file -encoding utf8 (join-path $PSScriptRoot "results.json")

$results | select -expand generalDiagnostics | ? { $_.severity -eq "error" } | out-host


# $results | select summary | ft -auto

