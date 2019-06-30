from m5stack import *
import network
import utime as time 

lcd.clear()

sta = network.WLAN(network.STA_IF)
sta.active(True)

while True:
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.print('wifi scan:')
    wifi_list = sta.scan()

    number = 1
    for i in wifi_list:
        lcd.print(i[0].decode(), 20, number*13)
        number += 1

    time.sleep(10)
