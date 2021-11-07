
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

Import-Module ..\..\FIRMWARE\get-serialport.ps1

function run_stubber {
    param( 
        $type = "minified",
        $serialport = "COM5"
    )
    
    switch ($type) {
        #condition {  }
        "minified" {
            $createstubs_py = join-path $WSRoot "minified/createstubs.py" 
            pyboard --device $serialport $createstubs_py | write-host
            # 0 = Success
            return $LASTEXITCODE -eq 0
        }
        Default {
            Write-Host "Sorry only minified is implemented"
            return $false
            # mpremote cp createstubs.py logging.py :
            # pyboard --device $serialport -f cp createstubs.py logging.py  :
            # rshell  -p $serialport --buffer-size 512 cp createstubs.py /pyboard 
            # rshell -p $serialport --buffer-size 512 cp logging.py /pyboard 

            # mpremote exec "import createstubs"
            # pyboard --device $serialport -c "import createstubs"
            # cd $PSScriptRoot
        }
    }
} 

function download_stubs {
    param (
        [Parameter(Mandatory = $true)]
        $path ,
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
    $source = "/pyboard/stubs"
    $n= 1
    do {
        rshell -p $serialport --buffer-size 512 rsync $source $subfolder  | write-host
        $n += 1
    } until ($LASTEXITCODE -eq 0 -or $n -eq 3)
    
    # restire cwd
    Pop-Location
    return $LASTEXITCODE -eq 0
}


function restart-MCU {
    [CmdletBinding()]
    param (
        [string]
        $serialport,
        [int]
        $delay = 3
    )
    # avoid MCU waiting in bootloader on hardware restart by setting both dtr and rts high
    start-sleep $delay
    rshell -p $serialport  --rts 1 repl "~ print('connected') ~"  | write-host
    rshell -p $serialport  --rts 1 repl "~ import machine ~ machine.reset() ~" | write-host
    Write-Host -F Yellow "Exitcode: $LASTEXITCODE"
    start-sleep $delay
    # esptool -p $serialport --chip esp32 --before usb_reset --after hard_reset run 
    if ($LASTEXITCODE -ne 0) {
        $n = 1
        do {
            Write-host "attempting to connect / reset : $n"
            $n = $n + 1
            rshell -p $serialport --quiet --rts 1 repl "~ print('connected') ~"
            Write-Host -F Yellow "Exitcode: $LASTEXITCODE"
            Write-Host -F Yellow "result  : $result"
        } until ($LASTEXITCODE -eq 0 -or $n -gt 3 )
        if ($LASTEXITCODE -ne 0) {
            Write-Host -F Red "this FW $version is a dud, try next"
            return $false
        }
    }
    return $true
}

# Save this spot
Push-Location -StackName "start-remote-stubber"

# $cwd = Get-Location
$WSRoot = "C:\develop\MyPython\micropython-stubber"
$download_path = (join-path -Path $WSRoot -ChildPath "stubs/machine-stubs")

Clear-Host 
Write-Host -ForegroundColor Cyan "Detecting devices...."

$devices = Get-SerialPort -chip  | Where-Object { $_.chip -and $_.chip.ToLower().StartsWith('esp') }
if (-not $devices) {
    Write-Error "No ESP devices connected"
    exit -1
}
else {
    $devices | Select -Property Chip, Port, Service , Description | Out-Host
}


$all_versions = @( 
    @{version = "v1.10"; chip = "esp8266"; },
    @{version = "v1.10"; chip = "esp32"; },
    @{version = "v1.11"; chip = "esp32"; },
    @{version = "v1.12"; chip = "esp32"; },
    @{version = "v1.13"; chip = "esp32"; nightly = $true },
    @{version = "v1.14"; chip = "esp32"; },
    @{version = "v1.15"; chip = "esp32"; },
    @{version = "v1.16"; chip = "esp32"; },
    @{version = "v1.17"; chip = "esp32"; }
)

$done = @()
    
foreach ($fw in $all_versions) {
        
    $device = $devices | Where-Object { $_.chip -and $_.chip.ToLower() -eq $fw.chip } | Select-Object -First 1
    if (-not $device) {
        Write-Warning "No '$($fw.chip)' device connected , skipping Flashing firmware $($fw.chip) $($fw.version) "
        continue
            
    }
    $serialport = $device.port
    Write-Host -ForegroundColor Cyan "Found an $($device.chip) device connected to $serialport"
    # 1) Flash a firmware 
    Write-Host -ForegroundColor Cyan "$($serialport, $fw.chip, $fw.version) - Flashing firmware on the device"
    
    ..\..\FIRMWARE\flash_MPY.ps1 -serialport $serialport -KeepFlash:$false  @fw
    
    # 2) restart MCU
    Write-Host -ForegroundColor Cyan "$($serialport, $fw.chip, $fw.version) - Restart device after flashing ..."
    $OK = restart-MCU -serialport $serialport
    if (-not $OK) {
        Write-Warning "$($serialport, $fw.chip, $fw.version) -Problem restarting the MCU "
    }
    # 3) upload & run stubber
    Write-Host -ForegroundColor Cyan "Starting createstubs.py"
    $OK = run_stubber -serialport $serialport
    if (-not $OK) {
        Write-Warning "$($serialport, $fw.chip, $fw.version) - Problem running Stubber"
        continue
    }

    # 4) download the stubs 

    Write-Host -ForegroundColor Cyan "$($serialport, $fw.chip, $fw.version) - Downloading the machine stubs"
    $OK = download_stubs -serialport $serialport -path $download_path
    if (-not $OK) {
        Write-Warning "$($serialport, $fw.chip, $fw.version) - Problem downloading the machine stubs"
        continue
    } 
    # Add to done
    $done += $fw

}

Pop-Location  -StackName "start-remote-stubber"

Write-host -ForegroundColor Cyan "Finished processing, and succeded generatign and downloading :"
$done | FL | Out-Host