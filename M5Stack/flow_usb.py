from m5stack import *
import m5base
import m5ucloud

lcd.clear()
__VERSION__ = m5base.get_version()
# Reset apikey
if btnB.isPressed():
    try:
        machine.nvs_erase('apikey.pem')
    except:
        pass
        
# M5Cloud
lcd.clear(lcd.BLACK)
lcd.font(lcd.FONT_DejaVu24)
lcd.fillRect(0, 0, 320, 30, 0x5757fc)
lcd.setTextColor(lcd.WHITE, 0x5757fc)
lcd.print("USB Mode", 5, 5, lcd.WHITE)

# apikey qrcode
lcd.font(lcd.FONT_DejaVu18)
lcd.setTextColor(0xaaaaaa, lcd.BLACK)
lcd.print(__VERSION__, 29, 80)
lcd.println("APIKEY", 27, 115)
lcd.font(lcd.FONT_DejaVu24)
# lcd.print(apikey, 12, 148, color=lcd.ORANGE)
lcd.print(apikey[:3], 35, 140, color=lcd.ORANGE)
lcd.print(apikey[3:], 20, 166, color=lcd.ORANGE)
lcd.qrcode("'https://m5stack.oss-cn-shenzhen.aliyuncs.com/video/%E6%95%99%E7%A8%8B/UIFlow%20Tutorials/A3%20-%20UIflow%20Tutorial%201.mp4", 126, 46, 175)

cloud = m5ucloud.M5UCloud()
cloud.run()