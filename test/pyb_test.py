# test of pyb stub file
import pyb

x = pyb.ADC

pyb.stop()

pyb.hard_reset()



i2c = pyb.I2C()
i2c.init('x')

c = pyb.CAN()
c.init()


import sys; sys.path.insert(1,"C:\\develop\\MyPython\\Stubber\\stubs\\esp32_LoBo_3_2_24")

sys.path


