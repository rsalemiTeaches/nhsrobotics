# Project 15: The Eye of the Alvik - Vision Test (SOLUTION)
#
# This code connects the HuskyLens and prints the ID of any
# AprilTag it sees to the console.
#
# It also changes the LED color:
# ID 1 = Green
# ID 2 = Blue
# Other ID = Red

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
# Import the HuskyLens library
from qwiic_huskylens import QwiicHuskylens
# Import the special I2C driver for Alvik
from qwiic_i2c.micropython_i2c import MicroPythonI2C

# --- Setup ---
print("Starting Project 15: Vision Test...")

# 1. Initialize the Robot
alvik = ArduinoAlvik()
alvik.begin()

# 2. Initialize the HuskyLens
# Create the special I2C driver.
# Remember: SCL is Pin 12, SDA is Pin 11.
alvik_i2c_driver = MicroPythonI2C(scl=12, sda=11)

# Create the HuskyLens object using that driver.
huskylens = QwiicHuskylens(i2c_driver=alvik_i2c_driver)

# Check connection
if not huskylens.begin():
    print("HuskyLens connection FAILED! Check wiring.")
    # Stop the program if the camera isn't found
    while True: 
        alvik.left_led.set_color(1, 0, 0) # Red Error Light
        sleep_ms(100)
        alvik.left_led.set_color(0, 0, 0)
        sleep_ms(100)
else:
    print("HuskyLens Connected!")
    # Flash Green to show success
    alvik.left_led.set_color(0, 1, 0)
    alvik.right_led.set_color(0, 1, 0)
    sleep_ms(500)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)

# 4. Set the Algorithm to Tag Recognition
# We want to detect AprilTags, not just colors.
# Note: We use the constant from the CLASS, not the object instance.
# If this fails, try using the integer 5 directly.
try:
    huskylens.set_algorithm(QwiicHuskylens.ALGORITHM_TAG_RECOGNITION)
except AttributeError:
    # Fallback if the constant name is different in this library version
    print("Warning: Constant not found, trying raw ID 5 for Tag Recognition")
    huskylens.set_algorithm(5)

sleep_ms(1000)
print("Setup Complete. Point camera at a tag.")

try:
    while not alvik.get_touch_cancel():
        
        # --- SENSE ---
        # Ask the camera what it sees
        # request_blocks() returns a list of objects seen
        huskylens.request_blocks()
        
        # --- THINK & ACT ---
        
        # Check if any blocks were seen
        if huskylens.blocks:
            # Get the first block seen
            # block = huskylens.blocks[0]
            
            # Get the ID of the tag (e.g., 1, 2, 3)
            # Note: In some library versions it is .ID, in others .id
            # We check both to be safe, though usually it's .ID
            try:
                tag_id = block.ID
            except AttributeError:
                tag_id = block.id
            for block in huskylens.blocks:
              # Display on Console (Shell)
              print(f"Tag ID Found: {tag_id}")
              print(f"Width: {block.width}")
              print(f"Height: {block.height}")
              print(f"XCenter: {block.xCenter}")
              print(f"YCenter: {block.yCenter}")
            # Change LEDs based on ID
            if tag_id == 1:
                # Green for Tag 1 ("Target Alpha")
                alvik.left_led.set_color(0, 1, 0)
                alvik.right_led.set_color(0, 1, 0)
            elif tag_id == 2:
                # Blue for Tag 2 ("Target Beta")
                alvik.left_led.set_color(0, 0, 1)
                alvik.right_led.set_color(0, 0, 1)
            else:
                # Red for unknown tags
                alvik.left_led.set_color(1, 0, 0)
                alvik.right_led.set_color(1, 0, 0)
                
        else:
            # Nothing seen
            # print("Scanning...") # Commented out to avoid spamming console
            # Turn LEDs off so we know it lost the target
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)

        # Small delay to keep the loop running smoothly
        sleep_ms(50)

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Stopping program.")
    alvik.stop()
    # Turn off LEDs
    alvik.left_led.set_color(0,0,0)
    alvik.right_led.set_color(0,0,0)