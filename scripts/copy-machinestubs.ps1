

# todo: find WSroot automatically
$WSRoot = "C:\develop\MyPython\micropython-stubber"

$download_path = (join-path -Path $WSRoot -ChildPath "stubs/machine-stubs")
$stub_path = (join-path -Path $WSRoot -ChildPath "all-stubs")

# folder are deep down
$folders = Get-ChildItem ( join-path $download_path "stubs" ) -Directory

foreach ($folder in $folders) {
    $TargetFolder = Join-Path $stub_path  $folder.BaseName
    mkdir $TargetFolder -Force -ErrorAction SilentlyContinue | Out-Null
    # remove all .py and .pyi files in the target folder 
    Get-ChildItem $TargetFolder -recurse -include *.py,*.pyi -force | remove-item -Force
    # now copy in the new stuff 
    Copy-Item -Path $folder -Destination $stub_path -recurse -Force -Container -PassThru
}
