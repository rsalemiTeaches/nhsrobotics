# This program tests the set_rgb function of the NanoLED class.
# It assumes the library is saved in a file named "nanolib_updated.py"
# in the same directory.

# Import the necessary libraries
from nanolib_updated import NanoLED
import time

def test_set_rgb():
    """
    Cycles through various colors to test the set_rgb() function.
    """
    print("Initializing NanoLED...")
    # Create a single instance of the NanoLED
    led = NanoLED()

    try:
        print("Setting brightness to 50% for the test.")
        led.set_brightness(50)
        time.sleep(1)

        print("Testing Red (255, 0, 0)")
        led.set_rgb(255, 0, 0)
        time.sleep(2)

        print("Testing Green (0, 255, 0)")
        led.set_rgb(0, 255, 0)
        time.sleep(2)

        print("Testing Blue (0, 0, 255)")
        led.set_rgb(0, 0, 255)
        time.sleep(2)

        print("Testing Purple (128, 0, 255)")
        led.set_rgb(128, 0, 255)
        time.sleep(2)

        print("Testing Orange (255, 165, 0)")
        led.set_rgb(255, 165, 0)
        time.sleep(2)

        print("Testing Cyan (0, 255, 255)")
        led.set_rgb(0, 255, 255)
        time.sleep(2)
        
        print("Test complete.")

    finally:
        # This block ensures the LED is turned off even if the program
        # is interrupted (e.g., by Ctrl+C).
        print("Turning LED off.")
        led.off()

# Run the test function
if __name__ == "__main__":
    test_set_rgb()