#############################
#         Project 05        #
#   Simple Line Follower    #
#############################

# In this project, you will teach your Alvik to follow a line.
# This is a classic robotics challenge that requires the robot
# to constantly Sense, Think, and Act in a loop.

# We will separate the "Thinking" part of our robot into its
# own function. This makes our code clean, easy to read,
# and easy to upgrade later!

from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# --- Configuration ---
# You can tune these values to change the robot's behavior.
BASE_SPEED = 25       # The robot's default speed when going straight.
TURN_ADJUSTMENT = 15  # How much to adjust the speed to make a turn.
BLACK_THRESHOLD = 500 # A sensor reading higher than this is considered "on the black line".

# --- The "Thinking" Function ---
# This function contains the simple logic for following the line.
# It takes the three sensor readings and decides how much to turn.
# It returns a single number: the "adjustment" value.
def get_turn_adjustment(left_val, center_val, right_val):
    """
    Calculates a turn adjustment value using simple if/elif/else logic.
    - Returns a positive value to turn right.
    - Returns a negative value to turn left.
    - Returns 0 to go straight.
    """
    
    # Is the LEFT sensor on the black line?
    if left_val > BLACK_THRESHOLD:
        # We are too far to the right. We need to turn LEFT.
        # Return a NEGATIVE adjustment value.
        return -TURN_ADJUSTMENT
        
    # Is the RIGHT sensor on the black line?
    elif right_val > BLACK_THRESHOLD:
        # We are too far to the left. We need to turn RIGHT.
        # Return a POSITIVE adjustment value.
        return TURN_ADJUSTMENT
        
    # If neither the left nor right sensor is on the line,
    # we assume the center one is, so we go straight.
    else:
        # Go straight. No adjustment needed.
        return 0

# --- Main Program ---
alvik = ArduinoAlvik()

try:
    alvik.begin()

    print("Project 05: Simple Line Follower")
    print("Place the robot on the line. The LEDs will blink blue.")
    print("Press the OK button to start.")
    
    # Wait for the user to press the OK button to begin.
    # The blinking LEDs provide a visual cue that the robot is ready.
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
        
        # Also check for cancel button while waiting
        if alvik.get_touch_cancel():
            # Break out of the waiting loop to go to the finally block
            raise KeyboardInterrupt 

    print("Starting...")

    # --- Main Loop ---
    while True:
        # Check for the cancel button to stop the program.
        if alvik.get_touch_cancel():
            break

        # 1. SENSE: Get the readings from the three line sensors.
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()

        # 2. THINK: Call our function to get the turn adjustment value.
        adjustment = get_turn_adjustment(l_sensor, c_sensor, r_sensor)

        # 3. ACT: Apply the adjustment to the motors.
        #    - To turn right (positive adjustment): left wheel speeds up, right wheel slows down.
        #    - To turn left (negative adjustment): left wheel slows down, right wheel speeds up.
        left_motor_speed = BASE_SPEED + adjustment
        right_motor_speed = BASE_SPEED - adjustment
        
        alvik.set_wheels_speed(left_motor_speed, right_motor_speed)

        # A small delay is always good in a loop.
        sleep_ms(20)

finally:
    # Always stop the robot when the program ends.
    alvik.stop()
    print("Program stopped.")
