# Project 11: Hello, HuskyLens! - Solution
# Connect the HuskyLens and make the Alvik's LEDs react when
# it sees a specific colored block (trained as ID 1).

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
# CORRECTED: Import the QwiicHuskylens class
from qwiic_huskylens import QwiicHuskylens
# CORRECTED: Import the specific MicroPython I2C driver required by Qwiic
from qwiic_i2c.micropython_i2c import MicroPythonI2C

alvik = ArduinoAlvik()

# --- Initialization ---
try:
    alvik.begin()

    print("Initializing HuskyLens...")
    # CORRECTED: Create the Qwiic I2C driver instance first,
    # specifying the correct SCL (Pin 12) and SDA (Pin 11) pins for Alvik.
    alvik_i2c_driver = MicroPythonI2C(scl=12, sda=11)

    # CORRECTED: Pass the specific driver to the HuskyLens constructor.
    huskylens = QwiicHuskylens(i2c_driver=alvik_i2c_driver)

    # Initialize the HuskyLens connection and check for errors
    if not huskylens.begin():
       print("HuskyLens connection FAILED! Check wiring.")
       # Stop the program if the camera isn't found
       raise RuntimeError("Failed to connect to HuskyLens")
    else:
       print("HuskyLens Connected!")

    # Set the HuskyLens algorithm to Color Recognition
    algo = QwiicHuskylens.kAlgorithmColorRecognition
    if not huskylens.set_algorithm(algo):
        print("Failed to set algorithm!")
    else:
        print("Algorithm set to Color Recognition.")

    print("Setup complete. Looking for Color ID 1...")

    # --- Main Loop ---
    while not alvik.get_touch_cancel():

        # --- SENSE ---
        if not huskylens.request_blocks():
            print("Failed to request blocks!")
            sleep_ms(100)
            continue

        results = huskylens.blocks

        # --- THINK & ACT ---
        object_found = False
        if results:
            block = results[0]
            if block.id == 1:
                object_found = True

        # Update LEDs based on whether the object was found
        if object_found:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
        else:
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)

        sleep_ms(50)

finally:
    print("Program finished.")
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()

