"""
Module: 'example_sub_led' on esp8266 v1.11
"""
# MCU: (sysname='esp8266', nodename='esp8266', release='2.2.0-dev(9422289)', version='v1.11-8-g48dcbbe60 on 2019-05-29', machine='ESP module with ESP8266')
# Stubber: 1.1.0
CLIENT_ID = None

class MQTTClient:
    ''
    def _recv_len():
        pass

    def _send_str():
        pass

    def check_msg():
        pass

    def connect():
        pass

    def disconnect():
        pass

    def ping():
        pass

    def publish():
        pass

    def set_callback():
        pass

    def set_last_will():
        pass

    def subscribe():
        pass

    def wait_msg():
        pass


class Pin:
    ''
    IN = 0
    IRQ_FALLING = 2
    IRQ_RISING = 1
    OPEN_DRAIN = 2
    OUT = 1
    PULL_UP = 1
    def init():
        pass

    def irq():
        pass

    def off():
        pass

    def on():
        pass

    def value():
        pass

SERVER = '192.168.1.35'
TOPIC = None
led = None
machine = None
def main():
    pass

micropython = None
state = 0
def sub_cb():
    pass

ubinascii = None
