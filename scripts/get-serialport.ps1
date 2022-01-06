

function Get-SerialPort {
    param(
        [switch]
        $chip,
        [switch]
        $dump
    )

    $RE_port = [regex]"\(COM(.*)\)"
    $SerialPorts = Get-CimInstance -Query 'SELECT * FROM Win32_PnPEntity WHERE ClassGuid="{4d36e978-e325-11ce-bfc1-08002be10318}"' | 
    Select-Object Description, Name, PNPClass , Service , Status | 
    ForEach-Object {
        #Split out the comport
        $re = $RE_port.Match($_.Name)

        $port = $re.Captures[0].value
        $port = $port.Substring( 1, $port.Length - 2)
        Add-Member -InputObject $_ -MemberType NoteProperty -Name "Port" -Value $port 
        if ($chip) {
            # try to find chip type using ESPtool 
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
        Write-Output $_
    }
    return $SerialPorts
}
