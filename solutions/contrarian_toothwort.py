from arduino_alvik import ArduinoAlvik
import time

# Initialize Alvik
alvik = ArduinoAlvik()
alvik.begin()

try:
  
  while True:
      # Moves servo
      alvik.set_servo_positions(0,0)
      time.sleep(2)
      alvik.set_servo_positions(90,0)
      time.sleep(2)
      alvik.set_servo_positions(180,0)
      time.sleep(2)
      alvik.set_servo_positions(90,0)
      time.sleep(2)
      if alvik.get_button_cancel():
        break

finally:
  alvik.stop()
