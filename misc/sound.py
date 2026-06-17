from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# 1. Initialize the base Alvik robot
alvik = ArduinoAlvik()
alvik.begin()

# 2. Initialize the SuperBot
bot = SuperBot(alvik)

# 3. Check if the buzzer is connected and play a sound
if bot.buzzer:
    print("Playing sound effect...")
    # You can use the built-in effect constants
    bot.buzzer.play_effect(bot.buzzer.EFFECT_YES)
    
    # Wait a moment to let the sound finish
    time.sleep(1)
else:
    print("Buzzer not found!")

# 4. Properly stop the robot threads
alvik.stop()