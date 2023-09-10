# install the stubs in the typings folder of the different ports 


$version = "latest"
$flatversion = $version -replace "\.", "_"

# get the subdirectories of this directory
$folders = Get-ChildItem -Path .\snippets -Directory | Select-Object -ExpandProperty Name | where { $_ -ne ".vscode" }    

$defaultport = "esp32"
# loop over the subdirectories
foreach ($folder in $folders) {
    $typings_dir = ".\snippets\$folder\typings"
    $port = $folder
    if ($folder -in @("common", "stdlib", "wip_todo")) {
        $port = $defaultport
    }   
    $stub_source = ".\repos\micropython-stubs\publish\micropython-$flatversion-$port-stubs"

    echo "--------------------------------------------------------"
    echo "folder: $folder"
    echo "typings_dir: $typings_dir"
    echo "stubs_source: $stub_source"
    echo "--------------------------------------------------------"

    # remove the typings directory
    rd $typings_dir -r  -ea silentlycontinue

    # Newest stdlib
    # pip install -U --target $typings_dir --no-user .\repos\micropython-stubs\publish\micropython-stdlib-stubs

    # install the stubs in the typings folder of the different ports 
    pip install -U --target $typings_dir --no-user $stub_source .\repos\micropython-stubs\publish\micropython-stdlib-stubs
}


