
# requirements & dependencies
# Python 
# - esptool 
# - wheel (nice to have)
# - pyboard 
# - rshell
#
# PowerShell
# ../../Firmware
#  - get-serialport.ps1
#  - flash_MPY.ps1
# hardware 
# ESP32 board on USB + Serial drivers 
# ESP8266 board on USB + Serial drivers 

Import-Module .\get-serialport.ps1 -Force


function restart-MCU {
    [CmdletBinding()]
    param (
        [string]
        $serialport,
        $delay_1 = 5,
        $delay_2 = 2

    )
    # avoid MCU waiting in bootloader on hardware restart by setting both dtr and rts high
    start-sleep $delay_1
    python $pyboard_py --device $serialport --no-soft-reset -c "help('modules')" | Write-Host
    #rshell -p $serialport  --buffer-size 512 --rts 1 repl "~ print('connected') ~"  | write-host
    Write-Host -F Yellow "Exitcode: $LASTEXITCODE"
    $EXIT_1 = $LASTEXITCODE
    $n = 1
    do {
        start-sleep $delay_2
        python $pyboard_py --device $serialport --no-soft-reset -c "help('modules')" | Tee-Object -Variable out | write-host
        $EXIT_2 = $LASTEXITCODE
        $TracebackFound = ($out -join "").Contains('Traceback')
        Write-Host -F Yellow "Exitcode: $LASTEXITCODE"
        $n = $n + 1 
    } until (($EXIT_2 -eq 0 -and -not $TracebackFound) -or $n -gt 3)
    if ($LASTEXITCODE -ne 0) {
        Write-Host -F Red "this FW $version is a dud, try next"
        return $false
    }
    return $true
}

function run_stubber {
    param( 
        $chip = "",
        $serialport 
    )
    # TODO: refactor to :
    # - type: board/minified/compiled 
    # - variant : normal/mem/db
    # need to have a verson with no logging
    switch ($chip) {
        "esp8266" { 
            $type = "compiled" 
            $createstubs_py = join-path $WSRoot "minified/createstubs_mem.py" 
            $createstubs_mpy = join-path $WSRoot "minified/createstubs_mem.mpy" 
        }
        "esp32" { 
            $type = "run"
            # need to have a verson with no logging
            $createstubs_py = join-path $WSRoot "minified/createstubs.py" 
        }
        "needs_reset" { 
            $type = "database" 
            $createstubs_py = join-path $WSRoot "minified/createstubs_mem_db.py" 
            $createstubs_mpy = join-path $WSRoot "minified/createstubs_mem_db.mpy" 
        }

        Default { 
            $type = "minified"
            $createstubs_py = join-path $WSRoot "minified/createstubs.py" 
        }
    }
    
    $modulelist_txt = join-path $WSRoot "board/modulelist.txt" 

    switch ($type) {

        "minified" {
            

            # copy modulelist.txt to the board
            python $pyboard_py --device $serialport --no-soft-reset -f cp $modulelist_txt :modulelist.txt | Write-Host
            python $pyboard_py --device $serialport --no-soft-reset -f cp $createstubs_py :createstubs.py | Write-Host
            # run the minified & compiled version 
            python $pyboard_py --device $serialport --no-soft-reset -c  "import createstubs" | write-host
            # 0 = Success
            return $LASTEXITCODE -eq 0
        }
        "compiled" {
            # ref : https://docs.micropython.org/en/latest/reference/mpyfiles.html
            # MicroPython release  .mpy version
            # v1.12 and up          5
            # v1.11                 4
            # v1.9.3 - v1.10        3
            # v1.9 - v1.9.2         2
            # v1.5.1 - v1.8.7       0
            if ($False) {

                # # cross compile the minified version - squeeze out all bits
                # # https://docs.micropython.org/en/latest/library/micropython.html#micropython.opt_level
                # # &mpy-cross ../minified/createstubs.py -O3
                # # Set to 0O2 for a bit more error info
                write-host "mpy-cross compile : $createstubs_py --> $createstubs_mpy"
                &mpy-cross $createstubs_py -O2 -o $createstubs_mpy
            }

            write-host "Using compiled versions: $createstubs_mpy"
            # copy modulelist.txt to the board
            python $pyboard_py --device $serialport --no-soft-reset -f cp $modulelist_txt :modulelist.txt | Write-Host
            python $pyboard_py --device $serialport --no-soft-reset -f cp $createstubs_mpy :createstubs.mpy | Write-Host
            # run the minified & compiled version 
            python $pyboard_py --device $serialport --no-soft-reset -c  "import createstubs" | write-host
            # python $pyboard_py --device $serialport $createstubs_py | write-host
            # 0 = Success
            return $LASTEXITCODE -eq 0
        }
        "run" {
            #python $pyboard_py --device $serialport $createstubs_py | write-host
            # MISTERY:  needs some magic introduction by rshell to make rshells pyboard work 
            rshell -p $serialport  --rts 1 repl "~ print('connected') ~"  | write-host
            start-sleep 2
            # use RSHELL's pyboard 
            pyboard --device $serialport $createstubs_py | write-host
            # 0 = Success
            return $LASTEXITCODE -eq 0

        }
        Default {
            # copy modulelist.txt to the board
            python $pyboard_py --device $serialport --no-soft-reset -f cp $modulelist_txt :modulelist.txt | Write-Host
            python $pyboard_py --device $serialport --no-soft-reset -f cp $createstubs_py :createstubs.py | Write-Host
            # run the minified & compiled version 
            python $pyboard_py --device $serialport --no-soft-reset -c  "import createstubs" | write-host
            # python $pyboard_py --device $serialport $createstubs_py | write-host
            # 0 = Success
            return $LASTEXITCODE -eq 0

        }
    }
} 

function download_stubs {
    param (
        [Parameter(Mandatory = $true)]
        $path ,
        $source = "/pyboard/stubs",
        $subfolder = "stubs",
        $serialport = "COM5"
    )
    # Save cwd 
    Push-Location

    $folder = $path
    # create folder if needed
    if (-not (Test-path $folder)) {
        New-Item -ItemType Directory -Force -Path $folder
    }
    Set-Location $folder
    # reverse sync 
    # $dest = path relative to current directory
    # $source = path on board ( all boards are called pyboard) 
    
    write-host "> rshell -p $serialport --buffer-size 512 rsync $source $subfolder"
    $n = 1
    do {
        rshell -p $serialport --buffer-size 512 rsync $source $subfolder  | write-host
        $n += 1
    } until ($LASTEXITCODE -eq 0 -or $n -eq 3)
    
    # restore cwd
    Pop-Location
    return $LASTEXITCODE -eq 0
}

function DetectDevices {
    param (
    )
    Write-Host -ForegroundColor Cyan "Detecting devices...."
    # find ESP 
    $devices = Get-SerialPort -chip  
    $devices = $devices | Where-Object { $_.chip }
    # $devices = $devices | Where-Object { $_.chip -and $_.chip.ToLower().StartsWith('esp') }
    if (-not $devices) {
        Write-Error "No ESP devices connected"
    }
    return $devices
}

# todo: find WSroot automatically
$WSRoot = "C:\develop\MyPython\micropython-stubber"
function stub_all {
    param (
        $download_path = (join-path -Path $WSRoot -ChildPath "stubs/machine-stubs"),
        $pyboard_py = (join-path $WSRoot "src/libs/pyboard.py" ),
        $update_pyi_py = (join-path $WSRoot "src/update_pyi.py" )
    )
    

    # use the local microython pyboard script , not the old version from PyPi 
    # note multiple versions of pyboard are present 
    #  - micropython/tools/pyboard.py - has simple file transfer options 
    #  - rshell can copy folders 
    #  - pyboard is install as part of rshell but cannot copy files 

    Clear-Host 
    $devices = @(DetectDevices)
    $devices | FT -Property Port, Chip, Board | out-host

    $all_versions = @( 
        
        # Older versions need a different/older/specific version of mpy-cross cross compiler
        # TODO: add old versions of mpy-cross to tools
        # @{version = "v1.10"; chip = "esp8266"; } ,
        # @{version = "v1.11"; chip = "esp8266"; } ,
        # @{version = "v1.12"; chip = "esp8266"; }  fails on a memory error


        @{version = "v1.13"; chip = "esp8266"; nightly = $true }
        @{version = "v1.14"; chip = "esp8266"; } ,
        @{version = "v1.15"; chip = "esp8266"; } ,
        @{version = "v1.16"; chip = "esp8266"; } ,
        @{version = "v1.17"; chip = "esp8266"; } ,
        @{version = "v1.18"; chip = "esp8266"; } ,

        
        @{version = "v1.10"; chip = "esp32"; },
        @{version = "v1.11"; chip = "esp32"; },
        @{version = "v1.12"; chip = "esp32"; },
        @{version = "v1.13"; chip = "esp32"; nightly = $true },
        @{version = "v1.14"; chip = "esp32"; },
        @{version = "v1.15"; chip = "esp32"; },
        @{version = "v1.16"; chip = "esp32"; },
        @{version = "v1.17"; chip = "esp32"; },
        @{version = "v1.18"; chip = "esp32"; },


        @{version = "v1.10"; chip = "stm32"; }
        @{version = "v1.11"; chip = "stm32"; }
        @{version = "v1.12"; chip = "stm32"; }
        @{version = "v1.13"; chip = "stm32"; }
        @{version = "v1.14"; chip = "stm32"; }
        @{version = "v1.15"; chip = "stm32"; }
        @{version = "v1.16"; chip = "stm32"; }
        @{version = "v1.17"; chip = "stm32"; }
        @{version = "v1.18"; chip = "stm32"; }
    )

    # Sort by version, newest first
    $all_versions = $all_versions | sort -Property version , chip  -Descending 

    # $all_versions = @(     @{version = "v1.18"; chip = "esp32"; })


    $results = @()
    foreach ($fw in $all_versions) {

        $result = $fw
        $result.Flash = "-"
        $result.Reset = "-"
        $result.Stub = "-"
        $result.Download = "-"
        $result.Error = "-"
        $result.path = $null

        $device = $devices | Where-Object { $_.chip -and $_.chip.ToLower() -eq $fw.chip } | Select-Object -First 1
        if (-not $device) {

            $result.Error = "No '$($fw.chip)' device connected."
            Write-Warning $result.Error
            $results += $result
            continue
                
        }
        $serialport = $device.port
        Write-Host -ForegroundColor Cyan ("-" * 100)
        Write-Host -ForegroundColor Cyan "Found an $($device.chip) device connected to $serialport"
        ###################################################################################################
        # 1) Flash a firmware
        Write-Host -ForegroundColor Cyan ("-" * 100)
        Write-Host -ForegroundColor Cyan "Micropython $($fw.version) on $($fw.chip) connected to $serialport"
        Write-Host -ForegroundColor Cyan "Flash new firmware"

        switch -wildcard ($fw.chip) {
            "esp*" { 
                Write-Host -ForegroundColor Cyan "$($serialport, $fw.chip, $fw.version) - Flashing firmware on the device"
                $ret = ..\..\FIRMWARE\flash_MPY.ps1 -serialport $serialport -KeepFlash:$false  @fw
                if ($ret -ieq "OK") {
                    $result.Flash = $ret
                }
                else {
                    $result.Error = $ret
                }
            }
            "stm32" {
                Write-Host -ForegroundColor Cyan "$($serialport, $fw.chip, $fw.version) - Flashing firmware on the device"
                # TODO: KeepFLash / Erase 
                # TODO: Erase does NOT erase the SD Card 
                $ret = ..\..\FIRMWARE\flash_PYB11.ps1 -serialport $serialport  -version $fw.version -erase
                if ($ret -ieq "OK") {
                    $result.Flash = $ret
                }
                else {
                    $result.Error = $ret
                }

            }
            Default {
                Write-Warning "$($serialport, $fw.chip, $fw.version) - unknown chip type"
                $result.Flash = "Failed"

            }
        }
        if ($result.Flash -ine "OK" ) {
            # Flashing did not work, move on to the next
            # Add to done
            $results += $result
            continue
        }

        # 2) restart MCU
        Write-Host -ForegroundColor Cyan ("-" * 100)
        Write-Host -ForegroundColor Cyan "Micropython $($fw.version) on $($fw.chip) connected to $serialport"
        Write-Host -ForegroundColor Cyan "Restart $($device.chip) after flashing"
        switch -wildcard ($fw.chip) {
            "esp*" {
                # esp need some help after esptool is done with them 
                # todo: maybe split out esp32/esp8266 specifics
                Write-Host -ForegroundColor Cyan "$($serialport, $fw.chip, $fw.version) - Restart device after flashing ..."
                $OK = restart-MCU -serialport $serialport
                if (-not $OK) {
                    Write-Warning "$($serialport, $fw.chip, $fw.version) -Problem restarting the MCU "
                    $result.Reset = "?"
                }
                else {
                    $result.Reset = "OK"
                }
            }
            default {
                $result.Reset = "OK"
            }
        }

        ###################################################################################################
        # 3) upload & run stubber
        Write-Host -ForegroundColor Cyan ("-" * 100)
        Write-Host -ForegroundColor Cyan "Micropython $($fw.version) on $($fw.chip) connected to $serialport"
        Write-Host -ForegroundColor Cyan "Starting createstubs.py"
        

        $OK = run_stubber -serialport $serialport -chip $fw.chip
        if (-not $OK) {
            Write-Warning "$($serialport, $fw.chip, $fw.version) - Problem running Stubber"
            $result.Stub = "Error"
            $results += $result
            continue
        }
        else {
            $result.Stub = "OK"
        }
        
        ###################################################################################################
        # 4) download the stubs 
        Write-Host -ForegroundColor Cyan ("-" * 100)
        Write-Host -ForegroundColor Cyan "Micropython $($fw.version) on $($fw.chip) connected to $serialport"
        Write-Host -ForegroundColor Cyan "Download the stubs to $download_path"

        switch -wildcard ($fw.chip) {
            "esp*" {
                Write-Host -ForegroundColor Cyan "$($serialport, $fw.chip, $fw.version) - Downloading the machine stubs"
                $OK = download_stubs -serialport $serialport -path $download_path  
            }
            "stm32" {
                Write-Host -ForegroundColor Cyan "$($serialport, $fw.chip, $fw.version) - Downloading the machine stubs from SD card"

                $OK = download_stubs -serialport $serialport -path $download_path -source "/pyboard/sd/stubs"
            }
            #   default {}
        }
        if (-not $OK) {
            Write-Warning "$($serialport, $fw.chip, $fw.version) - Problem downloading the machine stubs"
            $result.Download = "Error"
            $results += $result
            continue
        } 
        $result.Download = "OK"

        # Add to done
        $result.path = $download_path
        $results += $result
    }

    return $results

}

 
# Save this spot
Push-Location -StackName "start-remote-stubber"
$results = stub_all
Pop-Location  -StackName "start-remote-stubber"

Write-host -ForegroundColor Cyan "Finished processing: flash, reset, stubbing  and download :"
# # Array of Dict --> Array of objects with props
$results2 = $results | ForEach-Object { new-object psobject -property $_ -ea SilentlyContinue }  
# basic output
$results2 | Format-Table -Property Version, Chip, Flash, Reset, Stub, Download, Error, Path| Out-Host
$results2 | ConvertTo-json | Out-File bulk_stubber.json


foreach ($result in $results) {
    Write-Host -ForegroundColor Cyan ("-" * 100)
    Write-Host -ForegroundColor Cyan "processing stubs in $($result.path)"
    if (len($result.path ) >0 ) {
        # now generate .pyi files 
        python $update_pyi_py $result.path 
        # and run black formatting across all 
        black $result.path 
    }
}


# basic output
$results2 | Format-Table -Property Version, Chip, Flash, Reset, Stub, Download, Error, Path| Out-Host
