from m5stack import *
from uiflow import *
from m5ui import *

import i2c_bus
setScreenColor(0x111111)
a = i2c_bus.get(i2c_bus.PORTA)
label1 = M5TextBox(16, 42, "Text", lcd.FONT_DejaVu56,0xFFFFFF, rotate=0)
while True:
    label1.setText(str(a.scan()))
    time.sleep_ms(100)