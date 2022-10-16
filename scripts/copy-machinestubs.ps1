[CmdletBinding()]
param (
    $download_path = (join-path -Path $WSRoot -ChildPath "minified/stubs")
)

# todo: find WSroot automatically
$WSRoot = "C:\develop\MyPython\micropython-stubber"

$stub_path = (join-path -Path $WSRoot -ChildPath "repos/micropython-stubs/stubs")

# folder are deep down
$folders = Get-ChildItem $download_path  -Directory

foreach ($folder in $folders) {
    $TargetFolder = Join-Path $stub_path  $folder.BaseName
    mkdir $TargetFolder -Force -ErrorAction SilentlyContinue | Out-Null
    # remove all .py and .pyi files in the target folder 
    Get-ChildItem $TargetFolder -recurse -include *.py, *.pyi -force | remove-item -Force
    # now copy in the new stuff 
    write-host "Copy from $folder.FullName to $TargetFolder"
    Copy-Item -Path $folder.FullName -Destination $stub_path -recurse -Force -Container # -PassThru
    stubber stub -s $TargetFolder
}
