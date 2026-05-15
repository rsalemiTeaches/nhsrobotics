# tests/run_regression.py

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import sys

# Append the root-level tests directory to the sys.path list
if "/tests" not in sys.path:
    sys.path.append("/tests")
from regression_utils import RegressionRunner
import regression_logic
import regression_hardware
import regression_peripherals

def main():
    print("Initializing Regression Suite...")

    # Initialize base hardware
    alvik = ArduinoAlvik()
    alvik.begin()

    # Initialize SuperBot wrapper
    bot = SuperBot(alvik)

    runner = RegressionRunner()

    print("\n--- Running Logic Tests ---")
    runner.run_test("Logic: Closest Distance Static", regression_logic.test_closest_distance_static)
    runner.run_test("Logic: Calculate Approach Vector", regression_logic.test_calculate_approach_vector, bot)

    print("\n--- Running Hardware Tests ---")
    runner.run_test("Hardware: NanoLED", regression_hardware.test_nano_led, bot)
    runner.run_test("Hardware: Sensor Yaw", regression_hardware.test_sensor_yaw, bot)
    runner.run_test("Hardware: Touch Buttons", regression_hardware.test_buttons, bot)
    runner.run_test("Hardware: Motor Drive", regression_hardware.test_motor_drive, bot)
    runner.run_test("Hardware: Motor Rotate", regression_hardware.test_motor_rotate, bot)

    print("\n--- Running Peripheral Tests ---")
    runner.run_test("Peripheral: OLED", regression_peripherals.test_oled, bot)
    runner.run_test("Peripheral: Buzzer", regression_peripherals.test_buzzer, bot)
    runner.run_test("Peripheral: HuskyLens", regression_peripherals.test_huskylens, bot)

    runner.print_summary()

if __name__ == "__main__":
    main()
