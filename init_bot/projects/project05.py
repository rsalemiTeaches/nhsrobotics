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
    
    # WORK: Write an if/elif/else statement to decide how to turn.
    # WORK:
    # WORK: IF the left_val is greater than BLACK_THRESHOLD:
    # WORK:   The robot is too far right. Return -TURN_ADJUSTMENT to turn left.
    # WORK:
    # WORK: ELIF the right_val is greater than BLACK_THRESHOLD:
    # WORK:   The robot is too far left. Return TURN_ADJUSTMENT to turn right.
    # WORK:
    # WORK: ELSE (if we are centered on the line):
    # WORK:   Return 0 to go straight.

    return 0 # WORK: Remove this line when you have added your if/elif/else block.


# --- Main Program ---
alvik = ArduinoAlvik()

try:
    alvik.begin()

    print("Project 05: Simple Line Follower")
    print("Place the robot on the line. The LEDs will blink blue.")
    print("Press the OK button to start.")
    
    # Wait for the user to press the OK button to begin.
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
    while True:
        if alvik.get_touch_cancel():
            break

        # 1. SENSE: Get the readings from the three line sensors.
        # WORK: Call the alvik.get_line_sensors() function.
        # WORK: Store the three return values in variables named l_sensor, c_sensor, and r_sensor.
        l_sensor, c_sensor, r_sensor = 0, 0, 0 # WORK: Replace this line with your code.

        # 2. THINK: Call our function to get the turn adjustment value.
        adjustment = get_turn_adjustment(l_sensor, c_sensor, r_sensor)

        # 3. ACT: Apply the adjustment to the motors.
        # WORK: Create two new variables: left_motor_speed and right_motor_speed.
        # WORK: To turn right (positive adjustment): left wheel speeds up, right wheel slows down.
        # WORK:   Calculate left_motor_speed = BASE_SPEED + adjustment
        # WORK: To turn left (negative adjustment): left wheel slows down, right wheel speeds up.
        # WORK:   Calculate right_motor_speed = BASE_SPEED - adjustment
        left_motor_speed = 0  # WORK: Replace this line with your calculation.
        right_motor_speed = 0 # WORK: Replace this line with your calculation.

        alvik.set_wheels_speed(left_motor_speed, right_motor_speed)

        sleep_ms(20)

finally:
    # Always stop the robot when the program ends.
    alvik.stop()
    print("Program stopped.")
