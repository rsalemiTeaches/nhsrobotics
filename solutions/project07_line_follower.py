#############################
#         Project 06        #
#   Smart Line Follower     #
#############################

# In this project, we upgrade the "brain" of our line follower.
# Instead of a simple if/else statement that can only turn
# left or right, we will use a "proportional" algorithm.

# This means the robot will make small, smooth steering corrections
# when it's only slightly off the line, and sharper turns when
# it's far off the line. This results in much better performance.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# --- Configuration ---
BASE_SPEED = 30       # The robot's default speed.
BLACK_THRESHOLD = 500 # A sensor reading higher than this is "black".


# --- The "Thinking" Function (Upgraded Brain) ---
# This function implements the proportional control algorithm.
# It is now a self-contained "black box". The main loop doesn't
# need to know HOW it works, only that it returns the correct
# adjustment for the motors.
def get_turn_adjustment(left_val, center_val, right_val):
    """
    Calculates a proportional turn adjustment value.
    This value represents the "error" or how far the robot
    is from the center of the line, multiplied by a gain
    factor (KP) to create a final control signal.
    """
    # These constants are tuning knobs for our algorithm. Since they
    # are only used for this specific logic, we define them inside
    # the function for good encapsulation.
    LINE_LOST_THRESHOLD = 100
    KP = 25.0 # The Proportional Gain constant.

    # Step 1: Get total sensor reading.
    sum_weight = left_val + center_val + right_val

    # If all sensors see white (the sum is very low), it means we
    # have lost the line. Return 0 so the robot goes straight.
    if sum_weight < LINE_LOST_THRESHOLD:
        return 0

    # Step 2: Calculate the weighted sum.
    sum_values = (left_val * 1) + (center_val * 2) + (right_val * 3)

    # Step 3: Find the line's center (the "centroid").
    centroid = sum_values / sum_weight

    # Step 4: Calculate the raw error.
    error = centroid - 2
    
    # Step 5: Calculate the final control signal by multiplying
    # the error by our tuning knob, KP.
    control_signal = error * KP

    return control_signal

# --- Main Program ---
alvik = ArduinoAlvik()

try:
    alvik.begin()

    print("Project 06: Smart Line Follower")
    print("Place the robot on the line. The LEDs will blink blue.")
    print("Press the OK button to start.")
    
    while True:
        if alvik.get_touch_ok():
            break
        # Blink the LEDs blue to show we are waiting
        alvik.left_led.set_color(0, 0, 1)
        alvik.right_led.set_color(0, 0, 1)
        sleep_ms(100)
        alvik.left_led.set_color(0, 0, 0)
        alvik.right_led.set_color(0, 0, 0)
        sleep_ms(100)

    print("Starting...")

    # --- Main Loop ---
    # NOTE: This loop is now identical to the loop from Project 05!
    # The only change needed to upgrade the robot was to swap out
    # the contents of the get_turn_adjustment function.
    while True:
        if alvik.get_touch_cancel():
            break

        # 1. SENSE: Get the readings from the three line sensors.
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()

        # 2. THINK: Call our function to get the proportional adjustment value.
        adjustment = get_turn_adjustment(l_sensor, c_sensor, r_sensor)
        
        # 3. ACT: Apply the adjustment to the motors.
        left_motor_speed = BASE_SPEED + adjustment
        right_motor_speed = BASE_SPEED - adjustment
        
        alvik.set_wheels_speed(left_motor_speed, right_motor_speed)

        sleep_ms(20)

finally:
    # Always stop the robot when the program ends.
    alvik.stop()
    print("Program stopped.")
