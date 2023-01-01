# the hello world of IoT
# This short script serves as a sanity check.
# It makes the onboard LED blink

# ref: https://docs.micropython.org/en/latest/rp2/quickref.html

import utime as time
from machine import Pin


# Blink

# led = Pin()
led = Pin(1, value=2)
led = Pin(13, Pin.OUT)


for _ in range(2):
    led.on()
    time.sleep_ms(250)
    led.off()
    time.sleep_ms(250)

# Timers

from machine import Timer

tim = Timer(period=5000, mode=Timer.ONE_SHOT, callback=lambda t: print(1))
tim.init(period=2000, mode=Timer.PERIODIC, callback=lambda t: print(2))


from machine import Timer

tim = Timer(period=5000, mode=Timer.ONE_SHOT, callback=lambda t: print(1))
tim.init(period=2000, mode=Timer.PERIODIC, callback=lambda t: print(2))

# UART
from machine import UART, Pin

uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
uart1.write("hello")  # write 5 bytes
uart1.read(5)  # read up to 5 bytes


# PWM

from machine import Pin, PWM

pwm0 = PWM(Pin(0))  # create PWM object from a pin
pwm0.freq()  # get current frequency
pwm0.freq(1000)  # set frequency
pwm0.duty_u16()  # get current duty cycle, range 0-65535
pwm0.duty_u16(200)  # set duty cycle, range 0-65535
pwm0.deinit()  # turn off PWM on the pin

# ADC
from machine import ADC, Pin

adc = ADC(Pin(26))  # create ADC object on ADC pin
adc.read_u16()  # read value, 0-65535 across voltage range 0.0v - 3.3v


# Software I2C

from machine import Pin, SoftI2C

i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100_000)

i2c.scan()  # scan for devices

i2c.readfrom(0x3A, 4)  # read 4 bytes from device with address 0x3a
i2c.writeto(0x3A, "12")  # write '12' to device with address 0x3a

buf = bytearray(10)  # create a buffer with 10 bytes
i2c.writeto(0x3A, buf)  # write the given buffer to the peripheral

# Hardware I2C
from machine import Pin, I2C

i2c = I2C(0)  # default assignment: scl=Pin(9), sda=Pin(8)
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400_000)

# I2S

from machine import I2S, Pin

i2s = I2S(0, sck=Pin(16), ws=Pin(17), sd=Pin(18), mode=I2S.TX, bits=16, format=I2S.STEREO, rate=44100, ibuf=40000)  # create I2S object
i2s.write(buf)  # write buffer of audio samples to I2S device

i2s = I2S(1, sck=Pin(0), ws=Pin(1), sd=Pin(2), mode=I2S.RX, bits=16, format=I2S.MONO, rate=22050, ibuf=40000)  # create I2S object
i2s.readinto(buf)  # fill buffer with audio samples from I2S device


# RTC
from machine import RTC

rtc = RTC()
rtc.datetime((2017, 8, 23, 2, 12, 48, 0, 0))  # set a specific date and
# time, eg. 2017/8/23 1:12:48
rtc.datetime()  # get date and time


# RTC
from machine import WDT

# enable the WDT with a timeout of 5s (1s is the minimum)
wdt = WDT(timeout=5000)
wdt.feed()

# OneWire
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

# NeoPixel

from neopixel import NeoPixel

pin = Pin(0, Pin.OUT)  # set GPIO0 to output to drive NeoPixels
np = NeoPixel(pin, 8)  # create NeoPixel driver on GPIO0 for 8 pixels
np[0] = (255, 255, 255)  # set the first pixel to white
np.write()  # write data to all pixels
r, g, b = np[0]  # get first pixel colour
