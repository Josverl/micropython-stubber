from micropython import const
import gc
import network
import machine
import unit
import ujson as json
import utime as time
from m5stack import *
from mstate import *
import i2c_bus


VERSION = "0.2.3"
COLOR_GRAY = const(0xd7ceca)

# -------- Neopixel LED ---------
ledbar = rgb


# ------------- I2C -------------
i2c = i2c_bus.get(i2c_bus.M_BUS)

# ------------ Loading flash ------------
circ_time = 0
pt = 0


def loading_animat():
    global circ_time, pt
    if time.ticks_ms() > circ_time:
        circ_time = time.ticks_ms() + 300
    else:
        return
    d = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    c = (0xd7ceca, 0xf5be2b)
    pt = pt + 1 if pt < 2 else 0
    lcd.circle(147, 201, 4, c[d[pt][0]], c[d[pt][0]])
    lcd.circle(159, 201, 4, c[d[pt][1]], c[d[pt][1]])
    lcd.circle(171, 201, 4, c[d[pt][2]], c[d[pt][2]])


# ================ Next Prew Machine =================
prew_state_list = (
    "GUIDE",
    "GUIDE_ON",
    "PREW_SPEAKER",
    "PREW_MICRO",
    "PREW_GYRO",
    "PREW_RGB",
    "GUIDE_UNIT",
    "PREW_ENV",
    "PREW_MOTION",
    "PREW_EXRGB",
    "PREW_IR",
    "PREW_ANGLE"#,
    #"PREW_R2CODE"
)

prewstate = MStateManager()

def idle_loop(obj):
    time.sleep_ms(10)

# -------- GUIDE ----------
def guide_start(obj):
    lcd.image(0, 0, '/flash/img/2-1.jpg', type=lcd.JPG)

prewstate.register("GUIDE", MState(start=guide_start, loop=idle_loop))

# -------- ON ------------
def guide_on_start(obj):
    lcd.image(0, 0, '/flash/img/2-2.jpg', type=lcd.JPG)

prewstate.register("GUIDE_ON", MState(start=guide_on_start, loop=idle_loop))

# -------- ON ------------
def guide_unit_start(obj):
    lcd.image(0, 0, '/flash/img/2-3.jpg', type=lcd.JPG)

prewstate.register("GUIDE_UNIT", MState(start=guide_unit_start, loop=idle_loop))
# -------- PREW_SPEAKER --------


def speaker_start(obj):
    lcd.image(0, 0, '/flash/img/3-1.jpg', type=lcd.JPG)
    obj['isPlaying'] = False
    obj['wav'] = None
    obj['i2s'] = None

def speaker_loop(obj):
    global ii2s
    import wave
    i2s = obj['i2s']
    wav = obj['wav']
    if obj['isPlaying']:
        while True:
            data = wav.readframes(256)
            if len(data) > 0:
                i2s.write(data)
            if btnA.isPressed() or btnB.wasPressed() or btnC.isPressed() or (len(data) <= 0):
                wav.close()
                i2s.deinit()
                obj['isPlaying'] = False
                break
    else:
        time.sleep_ms(10)
        if btnB.wasPressed() and (not obj['isPlaying']):
            wav = wave.open('res/mix.wav')
            from machine import I2S
            i2s = I2S(mode=I2S.MODE_MASTER |
                      I2S.MODE_TX | I2S.MODE_DAC_BUILT_IN)
            i2s.set_dac_mode(i2s.DAC_RIGHT_EN)
            i2s.sample_rate(wav.getframerate())
            i2s.bits(wav.getsampwidth() * 8)
            i2s.nchannels(wav.getnchannels())
            i2s.volume(70)
            while not btnB.isReleased():  # wait release button
                pass
            obj['i2s'] = i2s
            ii2s = i2s
            obj['wav'] = wav
            obj['isPlaying'] = True

def speaker_end(obj):
    try:
        obj['i2s'].deinit()
        obj['wav'].close()
    except:
        pass
    unit.deinit()    

prewstate.register("PREW_SPEAKER", MState(
    start=speaker_start, loop=speaker_loop, end=speaker_end))

# -------- PREW_MICRO --------

def micro_start(obj):
    lcd.image(0, 0, '/flash/img/3-2.jpg', type=lcd.JPG)
    dac = machine.DAC(25)
    dac.write(0)
    adc = machine.ADC(34)
    adc.atten(adc.ATTN_11DB)
    obj['adc'] = adc
    buffer = []
    for i in range(0, 55):
        buffer.append(0)
    obj['buf'] = buffer

def micro_loop(obj):
    adc = obj['adc']
    buffer = obj['buf']
    val = 0
    for i in range(0, 32):
        raw = (adc.readraw() - 1845) // 10
        if raw > 20:
            raw = 20
        elif raw < -20:
            raw = -20
        val += raw
    val = val // 32
    buffer.pop()
    buffer.insert(0, val)
    for i in range(1, 50):
        lcd.line(i*2+44, 120+buffer[i+1], i*2+44+2, 120+buffer[i+2], lcd.WHITE)
        lcd.line(i*2+44, 120+buffer[i],   i*2+44+2, 120+buffer[i+1], lcd.BLACK)

def micro_end(obj):
    obj['adc'].deinit()
    unit.deinit()
    obj = {}

prewstate.register("PREW_MICRO", MState(
    start=micro_start, loop=micro_loop, end=micro_end))

# -------- PREW_GYRO --------
_pos = [0, 0]

def ball_move(x, y):
    global _pos
    if x > 42:
        x = 42
    elif x < -42:
        x = -42
    if y > 42:
        y = 42
    elif y < -42:
        y = -42
    x += 93
    y += 93
    if (not x == _pos[0]) or (not y == _pos[1]):
        lcd.rect(_pos[0]-11, _pos[1]-11, 22, 22, lcd.WHITE, lcd.WHITE)  # clean
        lcd.circle(x, y, 10, lcd.BLACK, lcd.BLACK)  # draw
        _pos[0] = x
        _pos[1] = y

def gyro_start(obj):
	global _pos
	_pos = [0, 0]
	lcd.image(0, 0, '/flash/img/3-3.jpg', type=lcd.JPG)

	try:
		from mpu6050 import MPU6050
		obj['imu'] = MPU6050(i2c, accel_sf=10)
	except:
		from mpu9250 import MPU9250
		obj['imu'] = MPU9250(i2c)

	obj['buf'] = [[0, 0] for i in range(0, 6)]
	lcd.rect(65, 65, 60, 60, lcd.WHITE, lcd.WHITE)  # old pic dot clean

def gyro_loop(obj):
    imu = obj['imu']
    buffer = obj['buf']
    val_x = 0
    val_y = 0
    for i in range(0, 4):
        raw = imu.acceleration
        val_x += raw[0]
        val_y += raw[1]
    buffer.pop()
    buffer.insert(0, [int(val_x//4), int(val_y//4)])
    val_x = 0
    val_y = 0
    for i in range(0, 6):
        val_x += buffer[i][0]
        val_y += buffer[i][1]
    ball_move(val_x, -val_y)
    obj['buf'] = buffer

def gyro_end(obj):
    obj = {}
    unit.deinit()

prewstate.register("PREW_GYRO", MState(start=gyro_start, loop=gyro_loop, end=gyro_end))

# -------- RGB LED --------

def rgbled_start(obj):
    lcd.image(0, 0, '/flash/img/3-4.jpg', type=lcd.JPG)
    # np = machine.Neopixel(machine.Pin(15), 10)
    ledbar.setBrightness(1)
    ledbar.setColorFrom(1, 5, lcd.RED)
    ledbar.setColorFrom(6, 10, lcd.BLUE)
    # obj['np'] = np
    obj['upinc'] = True
    obj['led_right'] = 0

def rgbled_loop(obj):
    led_right = obj['led_right']
    # np = obj['np']
    if obj['upinc']:
        led_right += 3
        if led_right >= 255*4:
            led_right == 255*4
            obj['upinc'] = False
    else:
        led_right -= 3
        if led_right <= 1:
            led_right = 1
            obj['upinc'] = True
    ledbar.setBrightness(led_right//4)
    obj['led_right'] = led_right

def rgbled_end(obj):
    ledbar.setColorAll(0)
    unit.deinit()

prewstate.register("PREW_RGB", MState(start=rgbled_start, loop=rgbled_loop, end=rgbled_end))

# -------- PREW_ENV --------

def env_start(obj):
    lcd.image(0, 0, '/flash/img/3-5.jpg', type=lcd.JPG)
    lcd.font(lcd.FONT_Default)

def env_loop(obj):
    if i2c.is_ready(92):
        try:
            env = unit.get(unit.ENV, unit.PORTA)
            lcd.print("%.1f" % env.temperature+"'C", 210, 120)
            lcd.print("%.1f" % env.humidity+"%",     210, 138)
            lcd.print("%.1f" % env.pressure+"Pa",     208, 156)
        except:
            pass
    else:
        lcd.rect(205, 105, 70, 70, lcd.WHITE, lcd.WHITE)
    time.sleep(0.2)   

def env_end(obj):
    obj = {}
    unit.deinit()
    pass

prewstate.register("PREW_ENV", MState(start=env_start, loop=env_loop, end=env_end))

# -------- PREW_MOTION --------
def motion_start(obj):
    lcd.image(0, 0, '/flash/img/3-6.jpg', type=lcd.JPG)
    obj['pir'] = unit.get(unit.PIR, unit.PORTB)

def motion_loop(obj):
    if time.ticks_ms() % 200 == 0:
        val = obj['pir'].state
        if val:
            lcd.circle(230, 150, 20, lcd.RED, lcd.RED)
        else:
            lcd.circle(230, 150, 20, COLOR_GRAY, COLOR_GRAY)

def motion_end(obj):
    obj = {}
    unit.deinit()

prewstate.register("PREW_MOTION", MState(start=motion_start, loop=motion_loop, end=motion_end))

# TODO
# -------- PREW_ANGLE --------
def angle_start(obj):
    lcd.image(0, 0, '/flash/img/3-9.jpg', type=lcd.JPG)
    # np = machine.Neopixel(machine.Pin(15), 10)
    ledbar.setBrightness(0)
    ledbar.setColorAll(lcd.WHITE)
    # obj['np'] = np
    obj['angle'] = unit.get(unit.ANGLE, unit.PORTB)
    obj['prev'] = 0
    dac = machine.DAC(machine.Pin(25))
    dac.write(0)
    lcd.font(lcd.FONT_DejaVu24)

def angle_loop(obj):
    time.sleep(0.02)
    val = int(obj['angle'].read() * 100 / 1024)
    if not obj['prev'] == int(val):
        if obj['prev'] == 100:
            lcd.rect(195, 138, 80, 35, lcd.WHITE, lcd.WHITE)
        obj['prev'] = val
        # obj['np'].brightness(int(255*val//100))
        ledbar.setBrightness(int(255*val//100))
        lcd.print("%02d%%" % (int(val)), 200, 140, COLOR_GRAY)

def angle_end(obj):
    ledbar.setColorAll(lcd.BLACK)
    time.sleep(0.05)
    obj['angle'].deinit()
    unit.deinit()


prewstate.register("PREW_ANGLE", MState(start=angle_start, loop=angle_loop, end=angle_end))

# -------- PREW_EXRGB --------
def exrgb_start(obj):
    lcd.image(0, 0, '/flash/img/3-7.jpg', type=lcd.JPG)
    obj['rgb'] = unit.get(unit.NEOPIXEL, unit.PORTB, 9)
    obj['rgb'].setBrightness(125)

def exrgb_loop(obj):
    rgb = obj["rgb"]
    rgb.setColor(1, lcd.RED)
    rgb.setColor(2, lcd.GREEN)
    rgb.setColor(3, lcd.BLUE)
    rgb.setColor(4, lcd.RED)
    rgb.setColor(5, lcd.GREEN)
    rgb.setColor(6, lcd.BLUE)
    rgb.setColor(7, lcd.RED)
    rgb.setColor(8, lcd.GREEN)
    rgb.setColor(9, lcd.BLUE)
    time.sleep(0.2)

def exrgb_end(obj):
    obj = {}
    unit.deinit()
    time.sleep(0.03)

prewstate.register("PREW_EXRGB", MState(start=exrgb_start, loop=exrgb_loop, end=exrgb_end))
# TODO
# -------- PREW_IR --------
duty = 0
ir_out = None
def pwm_out(arg):
    global duty, ir_out
    if btnB.isPressed():
        duty = 10 if duty == 0 else 0 
    else:
        duty = 0 
    ir_out.duty(duty)

def ir_start(obj): 
    global ir_out
    ledbar.setBrightness(0)
    lcd.image(0, 0, '/flash/img/3-8.jpg', type=lcd.JPG)
    lcd.image(180, 80, '/flash/img/11aa.jpg', type=lcd.JPG)
    obj['rx'] = machine.Pin(36, machine.Pin.IN)
    obj['tx'] = machine.PWM(26, 38000, duty=0.2, timer=1)
    ir_out = obj['tx']
    obj['timer'] = machine.Timer(0)
    obj['timer'].init(period=100, mode=obj['timer'].PERIODIC, callback=pwm_out)
    obj['times'] = 0
    obj['val'] = 0


def ir_loop(obj):
    val = obj['rx'].value()
    if val != obj['val']:
        obj['val'] = val
        obj['times'] = 0
    else:
        obj['times'] += 1
    if obj['times'] > 10:
        lcd.image(180, 80, '/flash/img/11aa.jpg', type=lcd.JPG)
        ledbar.setColorAll(lcd.BLACK)
    else:
        lcd.image(180, 80, '/flash/img/11bb.jpg', type=lcd.JPG)
        ledbar.setColorAll(0xcc66cc)
    time.sleep(0.01)

def ir_end(obj):
    global ir_out
    obj['timer'].deinit()
    obj['tx'].deinit()
    ir_out = None
    ledbar.setColorAll(0)
    time.sleep(0.05)
    unit.deinit()

prewstate.register("PREW_IR", MState(start=ir_start, loop=ir_loop, end=ir_end))

pre_state = None
# -------- STA_NEXT_MACHINE -------
def machine_start():
    global pre_state
    pre_state = 0
    prewstate.start(prew_state_list[0])

def machine_loop():
    global pre_state
    now_state = pre_state
    if btnA.wasPressed():
        if now_state == 2:
            now_state = len(prew_state_list)-1
        elif now_state > 0:
            now_state -= 1
        pre_state = now_state
        prewstate.change(prew_state_list[now_state])
    elif btnC.wasPressed():
        if now_state < len(prew_state_list)-1:
            now_state += 1
        else:
            now_state = 2
        pre_state = now_state
        prewstate.change(prew_state_list[now_state])
    prewstate.run()

# ============= Start ==============
def start():
    global prewstate
    lcd.setBrightness(30)
    machine_start()
    while True:
        try:
            machine_loop()
        except Exception as e:
            time.sleep_ms(10)
            print('---- Exception ----')
            print(e)

lcd.set_bg(lcd.WHITE)
start()