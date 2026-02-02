#############################
#         Project 07        #
#      Sumo Bot Code        #
#############################

# It is time to combine all the skills
# you've learned to create an autonomous Sumo Bot.

# The robot will use a priority-based system to make decisions:
# 1. Highest Priority: Don't fall out of the ring!
# 2. Second Priority: If an opponent is seen, attack!
# 3. Default Action: If nothing else is happening, search.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# We need the distance helper function again
from nhs_robotics import get_closest_distance

# --- Configuration (Your Strategy!) ---
# Tune these values to change your robot's behavior.
SEARCH_SPEED = 30       # Speed when looking for an opponent.
ATTACK_SPEED = 60       # Full speed for pushing!
WHITE_THRESHOLD = 300   # A sensor value LOWER than this is the white edge.
ATTACK_DISTANCE = 25    # How close an opponent must be before attacking.

# --- Main Program ---
alvik = ArduinoAlvik()

try:
    alvik.begin()

    print("Project 07: Sumo Bot Challenge")
    print("Place the robot in the ring. The LEDs will blink blue.")
    print("Press the OK button to start the match!")

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

    print("Battle Start!")

    # --- Main Loop ---
    while True:
        if alvik.get_touch_cancel():
            break

        # 1. SENSE: Get data from all relevant sensors at the start of the loop.
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()
        raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r = alvik.get_distance()
        closest_distance = get_closest_distance(raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r)

        # 2. THINK & ACT: Use a priority-based if/elif/else structure.
        
        # PRIORITY 1: AVOID THE EDGE
        # WORK: Write an if statement that checks if l_sensor OR r_sensor
        # WORK: is LESS THAN the WHITE_THRESHOLD.
        if False: # WORK: Replace `False` with your condition.
            # Evasive Maneuver!
            # WORK: Make the robot back up at SEARCH_SPEED.
            # WORK: Use sleep_ms(500) to back up for half a second.
            
            # WORK: Make the robot turn by setting the wheels to spin in
            # WORK: opposite directions at ATTACK_SPEED.
            # WORK: Use sleep_ms(500) to turn for half a second.
            pass # WORK: Remove this when you add your code.

        # PRIORITY 2: ATTACK OPPONENT
        # WORK: Write an elif statement that checks if closest_distance
        # WORK: is LESS THAN ATTACK_DISTANCE.
        elif False: # WORK: Replace `False` with your condition.
            # Attack Maneuver!
            # WORK: Set both LEDs to RED.
            # WORK: Set both wheels to ATTACK_SPEED to charge forward.
            pass # WORK: Remove this when you add your code.

        # PRIORITY 3: SEARCH FOR OPPONENT
        # WORK: Write the final else block for the default action.
        else:
            # Search Maneuver!
            # WORK: Set both LEDs to GREEN.
            # WORK: Set both wheels to SEARCH_SPEED to drive forward.
            pass # WORK: Remove this when you add your code.

        sleep_ms(20)

finally:
    # Always stop the robot when the program ends.
    alvik.stop()
    print("Match Over.")
