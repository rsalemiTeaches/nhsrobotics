from arduino_alvik import ArduinoAlvik
import time
 
alvik = ArduinoAlvik()
alvik.begin()
 
print("Line sensor test running.")
print("Slide the robot's nose over WHITE field, then over a BLACK line.")
print("Press the Cancel (X) touch button to stop.")
print()
 
try:
    while not alvik.get_touch_cancel():
        left, center, right = alvik.get_line_sensors()
        print("left:", left, " center:", center, " right:", right)
        time.sleep(0.2)
finally:
    alvik.stop()
    print("Stopped.")