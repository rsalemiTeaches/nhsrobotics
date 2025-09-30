from arduino_alvik import ArduinoAlvik
from time import sleep
import sys

alvik = ArduinoAlvik()
alvik.begin()
sleep(5)

while True:
  #Drive forward
  alvik.set_wheels_speed(10,10)
  sleep(2)
  #Turn left
  alvik.set_wheels_speed(0,20)
  sleep(2)
  #Turn right
  alvik.set_wheels_speed(20,0)
  sleep(2)
  #Drive backwards
  alvik.set_wheels_speed(-10,-10)
  sleep(2)