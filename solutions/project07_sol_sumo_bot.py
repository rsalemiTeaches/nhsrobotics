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
        # Is either the left or right sensor seeing the white line?
        if l_sensor < WHITE_THRESHOLD or r_sensor < WHITE_THRESHOLD:
            # Evasive Maneuver!
            # Back up to get away from the edge.
            alvik.set_wheels_speed(-SEARCH_SPEED, -SEARCH_SPEED)
            sleep_ms(500) # Back up for half a second.
            
            # Turn to face the center of the ring again.
            alvik.set_wheels_speed(ATTACK_SPEED, -ATTACK_SPEED)
            sleep_ms(500) # Turn for half a second.

        # PRIORITY 2: ATTACK OPPONENT
        # If we are not at the edge, check for an opponent.
        elif closest_distance < ATTACK_DISTANCE:
            # Attack Maneuver!
            # Set LEDs to red to show we are in attack mode.
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            # Charge forward at full speed.
            alvik.set_wheels_speed(ATTACK_SPEED, ATTACK_SPEED)

        # PRIORITY 3: SEARCH FOR OPPONENT
        # If we are not at the edge and see no opponent, search.
        else:
            # Search Maneuver!
            # Set LEDs to green to show we are searching.
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
            # Drive forward at a moderate speed.
            alvik.set_wheels_speed(SEARCH_SPEED, SEARCH_SPEED)

        sleep_ms(20)

finally:
    # Always stop the robot when the program ends.
    alvik.stop()
    print("Match Over.")
