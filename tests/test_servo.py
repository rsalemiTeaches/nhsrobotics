from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms

# Initialize the base Alvik robot and start I2C
alvik = ArduinoAlvik()
alvik.begin()

# Initialize SuperBot helper
sb = SuperBot(alvik)

try:
    # Loop to sweep servo A from 0 to 180 degrees continuously
    while not alvik.get_touch_cancel():
        # Move from 0 to 180 degrees
        for angle in range(0, 181, 10):
            sb.log_info(angle)
            alvik.set_servo_positions(angle, 0) # Sets Servo A, keeps Servo B at 0
            sleep_ms(150)
            
        # Move from 180 down to 0 degrees
        for angle in range(180, -1, -10):
            sb.log_info(angle)
            alvik.set_servo_positions(angle, 0)
            sleep_ms(150)

finally:
    # Crucial cleanup: stop background software threads safely
    alvik.stop()
