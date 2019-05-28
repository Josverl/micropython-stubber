# This file is executed on every boot (including wake-boot from deepsleep)
import sys
import network
import time
import logging

sys.path.append('/flash/lib')
sys.path.append('/lib')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)   

# create station interface - Standard WiFi client 
wlan = network.WLAN(network.STA_IF) 

# activate the interface
wlan.active(True)

# connect to a known WiFi 
wlan.connect('MicroPython', 'MicroPython')   

# Note that this may take some time, so we need to wait 
# Wait 5 sec or until connected 
tmo = 50
while not wlan.isconnected():
    time.sleep_ms(100)
    tmo -= 1
    if tmo == 0:
        break

# prettyprint the interface's IP/netmask/gw/DNS addresses
config = wlan.ifconfig()
log.info("IP:{0}, Network mask:{1}, Router:{2}, DNS: {3}".format( *config ))
