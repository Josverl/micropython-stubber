

#TODO: The &MI_xx suffix is the subdevice identifier and not actually part of the Device ID 
$KnowDevices = @{
    "USB\VID_F055&PID_9800&MI_01"          = @{chip = "stm32"; board = "pybv11" }; # pybv11
    "USB\VID_2E8A&PID_0005&REV_0100&MI_00" = @{chip = "rp2"; };
    "USB\VID_2E8A&PID_0005&MI_00"          = @{chip = "rp2"; };
    "USB\VID_2E8A&PID_1003&MI_00"          = @{chip = "rp2" };
    "USB\VID_F055&PID_9800&MI_00"          = @{chip = "rp2" };
}

# $CLASS_SERIAL = "{4d36e978-e325-11ce-bfc1-08002be10318}"
# $CLASS_COMPOSITE = "{36fc9e60-c465-11cf-8056-444553540000}"

# Get-CimInstance -Query 'SELECT * , ClassGuid FROM Win32_PnPEntity WHERE ClassGuid="{36fc9e60-c465-11cf-8056-444553540000}"' |  select-object * | ogv

#define MICROPY_HW_BOARD_NAME          "Pimoroni Pico LiPo 16MB"
#define MICROPY_HW_USB_VID (0x2E8A)
#define MICROPY_HW_USB_PID (0x1003)

function Get-SerialPort {
    param(
        [switch]
        $chip,
        [switch]
        $dump
    )

    $RE_port = [regex]"\(COM(.*)\)"
    $CIMSerialPorts = Get-CimInstance -Query 'SELECT * FROM Win32_PnPEntity WHERE ClassGuid="{4d36e978-e325-11ce-bfc1-08002be10318}"' | 
    Select-Object Description, Name, PNPClass , Service , Status, HardwareID 

    $SerialPorts = @()
    ForEach ($sp in $CIMSerialPorts) {

        #Split out the comport
        $re = $RE_port.Match($sp.Name)

        $port = $re.Captures[0].value
        $port = $port.Substring( 1, $port.Length - 2)
        Add-Member -InputObject $sp -MemberType NoteProperty -Name "Port" -Value $port 
        if (-not $chip) {
            $SerialPorts += $sp
            continue
        }
        if ($dump) {
            Write-Host -f Gray $sp.HardwareID
        }

        # lookup of VID / PID 
        foreach ($id in $sp.HardwareID) {
            $boardinfo = $KnowDevices.($id.toUpper())
            if ($boardinfo) {
                foreach ($key in $boardinfo.Keys) {
                    Add-Member -InputObject $sp -MemberType NoteProperty -Name $key -Value $boardinfo[$key]
                }
                break
            }
        }

        #
        if ( $sp.PSobject.Properties.Name.Contains("chip")) { 

            $SerialPorts += $sp
            continue
        }
        # ESP??? - try to find chip type using ESPtool 
        $out = esptool -p $port --no-stub chip_id 2>&1
        if ($dump) {
            Write-Host -f Gray $out
        }
        $chip_id = ($out | select-string 'Detecting chip type...' | select -Last 1 ).Line
        if ($chip_id) {
            $chip_id = $chip_id.Replace("Detecting chip type... ", "")
            Add-Member -InputObject $sp -MemberType NoteProperty -Name "chip" -Value $chip_id 
            $SerialPorts += $sp
            continue
        }

        if ( $sp.PSobject.Properties.Name.Contains("chip")) { 
            $SerialPorts += $sp
            continue
        }

        # dont know
        Add-Member -InputObject $sp -MemberType NoteProperty -Name "chip" -Value ""
        $SerialPorts += $sp
    }

    return $SerialPorts
}

if ($False) {
    $ports = Get-SerialPort 
    $ports | Ft -Property port, chip, board | Out-Host
    
    $ports = Get-SerialPort -chip 
    $ports | Ft -Property port, chip, board | Out-Host
}


