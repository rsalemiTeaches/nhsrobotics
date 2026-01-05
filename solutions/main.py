# Project 18: HuskyLens Hardware Test
# Version: V1.3 (Hardware I2C Bus 1 - With Alvik Support)
#
# OBJECTIVE:
# 1. Initialize ArduinoAlvik system.
# 2. Setup Hardware I2C Bus 1 for HuskyLens.
# 3. Perform a monitored detection loop.
# 4. Ensure proper cleanup with alvik.stop().

from machine import I2C, Pin
from arduino_alvik import ArduinoAlvik
from qwiic_huskylens import QwiicHuskylens
from qwiic_i2c.micropython_i2c import MicroPythonI2C
import time
import sys

# --- INITIALIZE ALVIK ---
alvik = ArduinoAlvik()
alvik.begin()

print("--- HUSKYLENS BUS 1 TEST START ---")

try:
    # Give the system a moment to stabilize after begin()
    time.sleep(0.5)
    
    # 1. Initialize the physical hardware bus 1
    # On Nano ESP32/Alvik, I2C(1) is the physical hardware peripheral for pins 11/12.
    print("Initializing Hardware I2C Bus 1 (Pins 12/11)...")
    hw_bus = I2C(1, scl=Pin(12), sda=Pin(11), freq=100000)

    # 2. Setup Camera using Injection
    # Note: If micropython_i2c.py still has a line-continuation bug, 
    # the sys.print_exception below will confirm it.
    print("Injecting bus into MicroPythonI2C...")
    alvik_i2c = MicroPythonI2C(esp32_i2c=hw_bus)
    #alvik_i2c = MicroPythonI2C(scl=12, sda=11)
  
    
    huskylens = QwiicHuskylens(i2c_driver=alvik_i2c)
    
    print("Attempting huskylens.begin()...")
    if huskylens.begin():
        print("HuskyLens Connected Successfully!")
        alvik.left_led.set_color(0, 1, 0) # Green for success
    else:
        print("HuskyLens failed to respond.")
        alvik.left_led.set_color(1, 0, 0) # Red for failure
        raise Exception("HuskyLens Begin Failed")

    # 3. Short Detection Loop
    print("Reading detection data for 10 seconds...")
    start_time = time.time()
    while (time.time() - start_time) < 10:
        huskylens.request()
        blocks = huskylens.blocks
        print(f"Found {len(blocks)} blocks")
        
        # Flash right LED if something is seen
        if len(blocks) > 0:
            alvik.right_led.set_color(0, 0, 1) # Blue
        else:
            alvik.right_led.set_color(0, 0, 0)
            
        time.sleep(0.2)

    print("--- TEST PASSED ---")

except Exception as e:
    print("\n--- DETAILED EXCEPTION REPORT ---")
    sys.print_exception(e)
    print("---------------------------------\n")

finally:
    # 4. CLEANUP
    print("Stopping Alvik and cleaning up...")
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
    print("Test finished.")