
function get-devices() {
    $devices = @()
    $devs_txt = @(mpremote connect list) | Where-Object { $_.length -gt 4 }
    # then split each line into an arry of words
    foreach ($line in $devs_txt) {

        $parts = $line.split(" ")
        $devices += @{ serialport = $parts[0]; id = $parts[1]; usb_id = $parts[2] }
    }
    return @($devices)
}


$devices = get-devices | where { $_.serialport -ne "COM20" }
$deviceS | % { write-host $_.serialport }
sleep 2

$devices = $devices | Sort-Object -Property serialport -Descending
write-host "gather more information about the devices"
# this assumes they are running micropython
# get-info is a copy from from createstubs.py

foreach ($d in $devices) {
    $SP = $d.serialport
    write-host "gather more information about: $SP"
    mpremote connect $d.serialport exec "print('hello from $SP')"
}
exit 1

sleep 2

foreach ($d in $devices) {
    write-host "gather more information about:" $d.serialport
    $info = mpremote connect $d.serialport get-info
    $info = $info[0]
    write-host $info
    $info = $info | ConvertFrom-Json
    $d.machine = $info.machine
    $d.port = $info.port
    $d.ver = $info.ver
    $d.family = $info.family
}

# $deviceS | fl | out-host

foreach ($d in $devices) {
    write-host "Found $($d.serialport)|$($d.port)|$($d.family)|$($d.machine)"
    # mpremote connect $d.serialport reset
}


# $devices = $devices.where({ $_.port -eq "stm32" })

$d = $devices[0]
del cr*.py 

foreach ($d in $devices) {
    write-host -f green "Stubbing $($d.serialport)|$($d.port)|$($d.family)|$($d.machine)"
    # remove state file
    del modulelist.done -ErrorAction SilentlyContinue
    switch ($d.port) {
        "stm32" {
            write-host -f green "pyboard v1.1 remote"
            # repeat while mpremote returns an non-zero exit code
            do {
                mpremote connect $d.serialport mount . resume exec "import createstubs_db" 
            } while ($LASTEXITCODE -eq 1)
            continue
        }
        "esp8266" {
            write-host -f green "esp8266"
            # repeat while mpremote returns an non-zero exit code
            do {
                mpremote connect $d.serialport mount . resume exec "import createstubs_db" 
            } while ($LASTEXITCODE -eq 1)
            continue
        }
        "esp32" {
            write-host -f green "esp32"
            sleep 2
            do {
                mpremote connect $d.serialport mount . resume exec "import createstubs_db" 
            } while ($LASTEXITCODE -eq 1)       
            continue
        }
        "rp2" {
            do {
                mpremote connect $d.serialport mount . resume exec "import createstubs_db" 
            } while ($LASTEXITCODE -eq 1)
        }
        Default {
            write-host -f Magenta "unknown board type"
            mpremote connect $d.serialport mount . resume exec "import createstubs_mem"
        }
    }
}

stubber stub -s .\stubs





