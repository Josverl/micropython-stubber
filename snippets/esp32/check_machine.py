# board : ESP32
# ref : https://docs.micropython.org/en/latest/esp32/quickref.html
import utime as time

import machine

machine.freq()  # get the current frequency of the CPU
machine.freq(240000000)  # set the CPU frequency to 240 MHz


# Pins and GPIO
# Use the machine.Pin class:

from machine import Pin

p0 = Pin(0, Pin.OUT)  # create output pin on GPIO0
p0.on()  # set pin to "on" (high) level
p0.off()  # set pin to "off" (low) level
p0.value(1)  # set pin to on/high

p2 = Pin(2, Pin.IN)  # create input pin on GPIO2
print(p2.value())  # get value, 0 or 1

p4 = Pin(4, Pin.IN, Pin.PULL_UP)  # enable internal pull-up resistor
p5 = Pin(5, Pin.OUT, value=1)  # set pin high on creation

# UART (serial bus)
# See machine.UART.

from machine import UART

uart1 = UART(3, baudrate=9600, tx=33, rx=32)
uart1.write("hello")  # write 5 bytes
uart1.read(5)  # read up to 5 bytes

# PWM (pulse width modulation)¶

from machine import Pin, PWM

pwm0 = PWM(Pin(0))  # create PWM object from a pin
freq = pwm0.freq()  # get current frequency (default 5kHz)
pwm0.freq(1000)  # set PWM frequency from 1Hz to 40MHz

duty = pwm0.duty()  # get current duty cycle, range 0-1023 (default 512, 50%)
pwm0.duty(256)  # set duty cycle from 0 to 1023 as a ratio duty/1023, (now 25%)

duty_u16 = pwm0.duty_u16()  # get current duty cycle, range 0-65535
pwm0.duty_u16(2**16 * 3 // 4)  # set duty cycle from 0 to 65535 as a ratio duty_u16/65535, (now 75%)

duty_ns = pwm0.duty_ns()  # get current pulse width in ns
pwm0.duty_ns(250_000)  # set pulse width in nanoseconds from 0 to 1_000_000_000/freq, (now 25%)

pwm0.deinit()  # turn off PWM on the pin

pwm2 = PWM(Pin(2), freq=20000, duty=512)  # create and configure in one go
print(pwm2)  # view PWM settings


# ADC (analog to digital conversion)¶

from machine import ADC

adc = ADC(Pin(32))  # create ADC object on ADC pin
adc.read()  # read value, 0-4095 across voltage range 0.0v - 1.0v

adc.atten(ADC.ATTN_11DB)  # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
adc.width(ADC.WIDTH_9BIT)  # set 9 bit return values (returned range 0-511)
adc.read()  # read value using the newly configured attenuation and width


# Software SPI bus


from machine import Pin, SoftSPI

# construct a SoftSPI bus on the given pins
# polarity is the idle state of SCK
# phase=0 means sample on the first edge of SCK, phase=1 means the second
spi = SoftSPI(baudrate=100000, polarity=1, phase=0, sck=Pin(0), mosi=Pin(2), miso=Pin(4))

spi.init(baudrate=200000)  # set the baudrate

spi.read(10)  # read 10 bytes on MISO
spi.read(10, 0xFF)  # read 10 bytes while outputting 0xff on MOSI

buf = bytearray(50)  # create a buffer
spi.readinto(buf)  # read into the given buffer (reads 50 bytes in this case)
spi.readinto(buf, 0xFF)  # read into the given buffer and output 0xff on MOSI

spi.write(b"12345")  # write 5 bytes on MOSI

buf = bytearray(4)  # create a buffer
spi.write_readinto(b"1234", buf)  # write to MOSI and read from MISO into the buffer
spi.write_readinto(buf, buf)  # write buf to MOSI and read MISO back into buf

# Hardware SPI
from machine import Pin, SPI

hspi = SPI(1, 10000000)
hspi = SPI(1, 10000000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
vspi = SPI(2, baudrate=80000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))


# Software I2C

from machine import Pin, SoftI2C

i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)

i2c.scan()  # scan for devices

i2c.readfrom(0x3A, 4)  # read 4 bytes from device with address 0x3a
i2c.writeto(0x3A, "12")  # write '12' to device with address 0x3a


# Hardware I2C bus

from machine import Pin, I2C

i2c = I2C(0)
i2c = I2C(1, scl=Pin(5), sda=Pin(4), freq=400000)

# construct an I2C bus
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)


# I2S bus

from machine import I2S, Pin

i2s = I2S(0, sck=Pin(13), ws=Pin(14), sd=Pin(34), mode=I2S.TX, bits=16, format=I2S.STEREO, rate=44100, ibuf=40000)  # create I2S object
i2s.write(buf)  # write buffer of audio samples to I2S device

i2s = I2S(1, sck=Pin(33), ws=Pin(25), sd=Pin(32), mode=I2S.RX, bits=16, format=I2S.MONO, rate=22050, ibuf=40000)  # create I2S object
i2s.readinto(buf)  # fill buffer with audio samples from I2S device

# Real time clock (RTC)

from machine import RTC

rtc = RTC()
rtc.datetime((2017, 8, 23, 1, 12, 48, 0, 0))  # set a specific date and time
rtc.datetime()  # get date and time


# WDT (Watchdog timer)

from machine import WDT

# enable the WDT with a timeout of 5s (1s is the minimum)
wdt = WDT(timeout=5000)
wdt.feed()


# Deep-sleep mode

import machine

# check if the device woke from a deep sleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print("woke from a deep sleep")

# put the device to sleep for 10 seconds
machine.deepsleep(10000)

# SD card
import machine, os

# Slot 2 uses pins sck=18, cs=5, miso=19, mosi=23
sd = machine.SDCard(slot=1)

os.mount(sd, "/sd")  # mount
os.listdir("/sd")  # list directory contents
os.umount("/sd")  # eject

# OneWire driver

from machine import Pin
import onewire

ow = onewire.OneWire(Pin(12))  # create a OneWire bus on GPIO12
ow.scan()  # return a list of devices on the bus
ow.reset()  # reset the bus
ow.readbyte()  # read a byte
ow.writebyte(0x12)  # write a byte on the bus
ow.write(b"123")  # write bytes on the bus
ow.select_rom(b"12345678")  # select a specific device by its ROM code

# DS18S20 and DS18B20 devices:

import ds18x20

ds = ds18x20.DS18X20(ow)
roms = ds.scan()
ds.convert_temp()
time.sleep_ms(750)
for rom in roms:
    print(ds.read_temp(rom))


# Capacitive touch

from machine import TouchPad, Pin

t = TouchPad(Pin(14))
t.read()  # Returns a smaller number when touched
