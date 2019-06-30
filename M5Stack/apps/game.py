# rock, paper, scissors
from m5stack import *
import utime as time

ROCK = 0
PAPER = 1
SCISSORS = 2

rps_img = (
  'img/rock_128.jpg',
  'img/paper_128.jpg',
  'img/scissors_128.jpg'
)

lcd.clear(lcd.WHITE)

lcd.image(48, 200,  'img/rock_128.jpg', 2)
lcd.image(143, 200, 'img/paper_128.jpg', 2)
lcd.image(238, 200, 'img/scissors_128.jpg', 2)

def win_sound():
  speaker.tone(1046, 120, 1)
  speaker.tone(1175, 120, 1)
  speaker.tone(1318, 120, 1)
  speaker.tone(1976, 120, 1)

def lose_sound():
  speaker.tone(1976, 120, 1)
  speaker.tone(1318, 120, 1)
  speaker.tone(1175, 120, 1)
  speaker.tone(1046, 120, 1)

while True:
  rand = machine.random(2)
  lcd.image(lcd.CENTER, 30, rps_img[rand])

  if btnA.isPressed():   # ROCK
    if rand == SCISSORS:
      win_sound()
    elif rand == PAPER:
      lose_sound()
    while not btnA.isReleased(): # Wait for button A release
      pass

  elif btnB.wasPressed(): # PAPER
    if rand == ROCK:
      win_sound()
    elif rand == SCISSORS:
      lose_sound()
    while not btnB.isReleased(): # Wait for button B release
      pass

  elif btnC.wasPressed(): # SCISSORS
    if rand == PAPER:
      win_sound()
    elif rand == ROCK:
      lose_sound()
    while not btnC.isReleased(): # Wait for button C release
      pass
  
  time.sleep(0.02)

