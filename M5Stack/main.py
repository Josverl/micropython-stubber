from m5stack import *
from m5ui import *
from uiflow import *
setScreenColor(0x111111)

from numbers import Number

a = None
i = None

def PartA():
  global a, i
  global Number
  for i in range(106):
    wait(0.001)
    lcd.pixel(i, 110, 0x339999)
  for i in range(71):
    if i % 3 == 0:
      a = (a if isinstance(a, Number) else 0) + 1
    wait(0.001)
    lcd.pixel((105 + a), (110 - i), 0x33ffff)
  for i in range(141):
    if i % 3 == 0:
      a = (a if isinstance(a, Number) else 0) + 1
    wait(0.001)
    lcd.pixel((105 + a), (40 + i), 0x33ffff)
  for i in range(71):
    if i % 3 == 0:
      a = (a if isinstance(a, Number) else 0) + 1
    wait(0.001)
    lcd.pixel((105 + a), (180 - i), 0x33ffff)
  for i in range(121):
    wait(0.001)
    lcd.pixel((200 + i), 110, 0x339999)

def PartB():
  global a, i
  global Number
  for i in range(106):
    wait(0.001)
    lcd.pixel(i, 110, 0x000000)
  for i in range(71):
    if i % 3 == 0:
      a = (a if isinstance(a, Number) else 0) + 1
    wait(0.001)
    lcd.pixel((105 + a), (110 - i), 0x000000)
  for i in range(141):
    if i % 3 == 0:
      a = (a if isinstance(a, Number) else 0) + 1
    wait(0.001)
    lcd.pixel((105 + a), (40 + i), 0x000000)
  for i in range(71):
    if i % 3 == 0:
      a = (a if isinstance(a, Number) else 0) + 1
    wait(0.001)
    lcd.pixel((105 + a), (180 - i), 0x000000)
  for i in range(121):
    wait(0.001)
    lcd.pixel((200 + i), 110, 0x000000)

a = 0
speaker.setVolume(1)
while True:
  PartA()
  speaker.tone(1600, 100)
  a = 0
  PartB()
  a = 0
  wait(0.001)
