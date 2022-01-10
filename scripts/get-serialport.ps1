
function Get-SerialPort {
    param(
        [switch]
        $chip,
        [switch]
        $dump
    )

    $RE_port = [regex]"\(COM(.*)\)"
    $SerialPorts = Get-CimInstance -Query 'SELECT * FROM Win32_PnPEntity WHERE ClassGuid="{4d36e978-e325-11ce-bfc1-08002be10318}"' | 
    Select-Object Description, Name, PNPClass , Service , Status, HardwareID | 
    ForEach-Object {
        #Split out the comport
        $re = $RE_port.Match($_.Name)

        $port = $re.Captures[0].value
        $port = $port.Substring( 1, $port.Length - 2)
        Add-Member -InputObject $_ -MemberType NoteProperty -Name "Port" -Value $port 
        if ($chip) {
            if ($dump) {
                Write-Host -f Gray $_.HardwareID
            }

            # TODO : refactor to nice lookup of VID / PID 
            # Pyboard
            foreach ($id in $_.HardwareID) {
                # Pyboard 
                if ($ID.startsWith("USB\VID_F055&PID_9800")) {
                    #TODO : determine Pyboard version 
                    Add-Member -InputObject $_ -MemberType NoteProperty -Name "Chip" -Value "pyb11" 
                    break
                }
            }
            #define MICROPY_HW_BOARD_NAME          "Pimoroni Pico LiPo 16MB"
            #define MICROPY_HW_USB_VID (0x2E8A)
            #define MICROPY_HW_USB_PID (0x1003)
            foreach ($id in $_.HardwareID) {
                # Pyboard 
                if ($ID.startsWith("USB\VID_2E8a&PID_1003")) {
                    Add-Member -InputObject $_ -MemberType NoteProperty -Name "Chip" -Value "Pico_LiPo_16MB"
                    break
                }
            }
            #--------------------------
            #define MICROPY_HW_USB_VID (0x2E8A) // Raspberry Pi
            #define MICROPY_HW_USB_PID (0x0005) // RP2 MicroPython

            if (-not $_.PSobject.Properties.Name.Contains("Chip")) {
                # ESP??? - try to find chip type using ESPtool 
                $out = esptool -p $port --no-stub chip_id 2>&1
                if ($dump) {
                    Write-Host -f Gray $out
                }
                $chip_id = $out | Where-Object { $_.StartsWith('Detecting chip type...') } | Select-Object -Last 1
                if ($chip_id) {
                    $chip_id = $chip_id.Replace("Detecting chip type... ", "")
                    Add-Member -InputObject $_ -MemberType NoteProperty -Name "Chip" -Value $chip_id 
                }
            }
        }
        Write-Output $_
    }
    return $SerialPorts
}
