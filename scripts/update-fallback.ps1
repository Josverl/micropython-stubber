


# todo: find WSroot automatically
$WSRoot = "C:\develop\MyPython\micropython-stubber"

$stub_path = (join-path -Path $WSRoot -ChildPath "all-stubs")
$fallback_path = (join-path -Path $stub_path -ChildPath "typings/fallback")

#
Get-ChildItem $fallback_path -recurse -include *.py, *.pyi -force | remove-item -Force

$source = @{ 
    "uasyncio"       = "micropython-v1_18-esp32";
    "umqtt"          = "micropython-v1_18-esp32";
    "_onewire.py"    = "micropython-v1_18-esp32";
    "_uasyncio.py"   = "micropython-v1_18-esp32";
    "array.py"       = "micropython-v1_18-esp32";
    "binascii.py"    = "micropython-v1_18-esp32";
    "esp.py"         = "micropython-v1_18-docstubs"; # esp32";
    "esp32.py"       = "micropython-v1_18-docstubs"; # esp32";

    "hashlib.py"     = "micropython-v1_18-esp32";
    "machine.py"     = "micropython-v1_18-esp32";
    "micropython.py" = "micropython-v1_18-docstubs"; # esp32";
    "network.py"     = "micropython-v1_18-docstubs"; # esp32";
    "os.py"          = "micropython-v1_18-esp32"; # -> stdlib 

    "struct.py"      = "micropython-v1_18-esp32";
    "sys.py"         = "micropython-v1_18-esp32";
    "time.py"        = "micropython-v1_18-esp32"; # -> stdlib
    "uarray.py"      = "micropython-v1_18-esp32";
    "ubinascii.py"   = "micropython-v1_18-esp32";
    "uctypes.py"     = "micropython-v1_18-esp32";
    "uerrno.py"      = "micropython-v1_18-esp32";
    "uhashlib.py"    = "micropython-v1_18-esp32";
    "uio.py"         = "micropython-v1_18-esp32";
    "ujson.py"       = "micropython-v1_18-esp32";
    "uos.py"         = "micropython-v1_18-esp32";
    "uselect.py"     = "micropython-v1_18-esp32";
    "usocket.py"     = "micropython-v1_18-esp32";
    "ussl.py"        = "micropython-v1_18-esp32";
    "ustruct.py"     = "micropython-v1_18-esp32";
    "usys.py"        = "micropython-v1_18-esp32";
    "utime.py"       = "micropython-v1_18-esp32";
    "uzlib.py"       = "micropython-v1_18-esp32";

    "pyb.py"         = "micropython-v1_18-pyboard";
    "framebuf.py"    = "micropython-v1_18-pyboard";

    "_rp2.py"        = "micropython-v1_18-rp2";

    "bluetooth.py"   = "micropython-v1_18-docstubs";
}

foreach ($name in $source.Keys) {
    if ( -not $name.contains('.')) {
        
        # folder
        echo "Copy $name from  $($source[$name])"
        $src = Join-Path $stub_path  -ChildPath "$($source[$name])/$name"
        Copy-Item $src $fallback_path -Recurse -force -PassThru 
        
    }
    else {
        # .py&.pyi file
        # echo "Copy $name from  $($source[$name])"
        $src = Join-Path $stub_path  -ChildPath "$($source[$name])/$($name)"
        Copy-Item $src $fallback_path -force -PassThru 
        $src = Join-Path $stub_path  -ChildPath "$($source[$name])/$($name)i"
        Copy-Item $src $fallback_path -force -PassThru 
    }
}


