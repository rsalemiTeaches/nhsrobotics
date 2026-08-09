# dev/line_sensor_probe.py -- read the line sensors, show them. V02

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

try:
    while not sb.held('cancel'):
        left, centre, right = alvik.get_line_sensors()
        print(left, centre, right)
        sb.update_display("L %s" % left, "C %s" % centre, "R %s" % right)
        time.sleep(0.2)

finally:
    alvik.stop()
