# get 
# simple in powershell, too complex in python 
$repo = "..\TESTREPO-micropython"
$tag = $args[0]
$current = $PWD
try {
    cd $repo
    $result = (&git switch -) 
    $result = (&git checkout tags/$tag) 
    cd $current
    return $true
} catch {
    cd $current
    return $false
} 
