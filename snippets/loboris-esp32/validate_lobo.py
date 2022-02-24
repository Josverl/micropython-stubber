# type: ignore
# TODO: LOBO - update firmware stubs


#----------
# Snippet: Get Network time 
# Lobo Specific 
#-----------
import machine,time

import machine

rtc = machine.RTC()
if not rtc.synced():
    my_timezone = "CET-1CEST" # found in second field, text before the coma, in https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/blob/master/MicroPython_BUILD/components/micropython/docs/zones.csv
    rtc = machine.RTC()
    rtc.init((2019, 1, 1, 12, 12, 12))
    rtc.ntp_sync(server= "", tz=my_timezone, update_period=3600)
#need to wait a bit 
while not rtc.synced():
  time.sleep_ms(10)
  
print(rtc.now())



#----------
# Snippet: FTP Server
# Lobo Specific 
#-----------
import network,time
network.ftp.start(user="micro", password="python")

time.sleep(1)
_=network.ftp.status()
print("FTP server: {}, {} on {}".format(_[2],_[3],_[4]))

#----------
# Snippet: Telnet Server
# Lobo Specific 
#-----------
import network
network.telnet.start(user="micro", password="python")

time.sleep(1)
_=network.telnet.status()
print("Telnet server: {} on {}".format(_[1],_[2]))


#----------
# Dir / ls 
# uses upysh modules (preloaded in LoBo) 
#-----------

if not 'ls' in dir():
    from upysh import *
ls

# Best practice in handling errors and logging: 
import logging 
logger = logging.getLogger(__name__)

#------------------------------
# mount SDCard [ LoBo] 
# SDCard configuration for M5Stack
# https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/wiki/filesystems 
#------------------------------
import uos as os
try:
    #crude way to detect if the sd is already loaded 
    _ = os.stat('/sd')
except OSError as e:
    _ = os.sdconfig(os.SDMODE_SPI, clk=18, mosi=23, miso=19, cs=4)
    _ = os.mountsd()


#------------------------------
#ESP32 logging handling [LoBo]
#ESP32 log messages can be disabled or enabled with the desired log level.
# todo: python / *nix error codes
# https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/wiki/machine#esp32-loging-handling 
#------------------------------
# Logging for the individual components or all components can be set.
# The following constants can be used for setting the log level:
# machine.LOG_NONE, machine.LOG_ERROR, machine.LOG_WARN
# machine.LOG_INFO, machine.LOG_DEBUG, machine.LOG_VERBOSE 
# machine.loglevel(component, log_level)
# Set the log level of the component to level log_level
# component is the name of the component as it apears in log messages.

# NOTE: '*' can be used to set the global log level.

import machine
machine.loglevel("wifi", machine.LOG_DEBUG)
machine.loglevel('*', machine.LOG_VERBOSE)
machine.loglevel('[modnetwork]', machine.LOG_DEBUG)
machine.loglevel('wifi', machine.LOG_DEBUG)
machine.loglevel('tcpip_adapter', machine.LOG_DEBUG)
machine.loglevel('event', machine.LOG_INFO)


#-------------------------------------------------------------------------
#--------------------------------------
# Get curent time from the internet - LoBo 
# Note : The Loboris firmware works different from standard Micropython 
# reference : https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/wiki/rtc
#--------------------------------------
from machine import RTC
import time
timezone = 'CET-1CEST'
rtc = RTC()
#Set the system time and date, (in this case very roughly).
rtc.init((2019, 1, 1, 12, 12, 12))
#configure to sync the time every hour with a Network Time Protocol (NTP) server
rtc.ntp_sync(server= "", tz=timezone, update_period=3600)

# It may take some time for the ntp server to reply, so we need to wait 
# Wait 5 sec or until time is synched 
tmo = 50
while not rtc.synced():
    utime.sleep_ms(100)
    tmo -= 1
    if tmo == 0:
        break
#get the current,synchonized, time 
rtc.now()
#-------------------------------------------------------------------------