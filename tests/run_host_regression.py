# tests/run_host_regression.py
#
# The laptop half of the regression suite. V01
#
#     python3 tests/run_host_regression.py
#
# Runs every test that needs no robot, using the same RegressionRunner and the
# same PASS/FAIL/SKIP output as run_regression.py. Use this before flashing a
# change to nhs_lib. run_regression.py runs these too, plus everything that
# needs real hardware.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

for path in (HERE, os.path.join(REPO, "nhs_lib")):
    if path not in sys.path:
        sys.path.insert(0, path)

from regression_utils import RegressionRunner
import regression_host


def main():
    print("Initializing Host Regression Suite (no robot required)...")

    runner = RegressionRunner()

    print("\n--- Running Host Tests ---")
    runner.run_test("Host: light_both_leds", regression_host.test_light_both_leds)
    runner.run_test("Host: Stick Deadzone", regression_host.test_stick_deadzone)
    runner.run_test("Host: Gamepad held/pressed", regression_host.test_gamepad_held_and_pressed)
    runner.run_test("Host: Touch held/pressed", regression_host.test_touch_held_and_pressed)
    runner.run_test("Host: Unknown Button Name", regression_host.test_unknown_button_name_raises)
    runner.run_test("Host: Closest valid distance", regression_host.test_closest_valid)

    runner.print_summary()
    return 1 if runner.fails else 0


if __name__ == "__main__":
    sys.exit(main())
