#############################
#         Project 08        #
#        The Guard Bot      #
#############################

# This project introduces a new, powerful programming concept:
# a "State Machine". A state machine allows a robot to have
# different behaviors, or "states," and switch between them
# based on sensor input.

# Our Guard Bot will have two states:
# 1. PATROLLING: It drives forward, "guarding" its area.
# 2. ALERT: If it sees an intruder, it stops, spins 3 times, and then
#    returns to patrolling.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
from nhs_robotics import get_closest_distance

# --- State Machine Definitions ---
# We define our robot's possible states as constants.
PATROLLING = 1
ALERT = 2

# --- Configuration ---
PATROL_SPEED = 25       # How fast the robot moves while on patrol.
ALERT_DISTANCE = 5      # How close an intruder must be to trigger an alert.
ALERT_SPINS = 3         # How many times the robot spins in alert mode.
SPIN_SPEED = 40         # How fast the robot spins.
ALERT_SPIN_DEGREES = 180 # How many degrees to spin to face away.

# --- Main Program ---
alvik = ArduinoAlvik()

# We need a variable to store the robot's current state.
# It will start in the PATROLLING state.
current_state = PATROLLING

# We need a counter for our alert action.
spin_counter = 0

try:
    alvik.begin()
    print("Project 08: The Guard Bot")
    print(f"Current State: PATROLLING")
    print("Press OK to begin the patrol!")

    while True:
        if alvik.get_touch_ok():
            break
        # Blink green to show it's ready to patrol
        alvik.left_led.set_color(0, 1, 0)
        alvik.right_led.set_color(0, 1, 0)
        sleep_ms(100)
        alvik.left_led.set_color(0, 0, 0)
        alvik.right_led.set_color(0, 0, 0)
        sleep_ms(100)

    print("Patrol started!")

    # --- Main Loop ---
    while True:
        if alvik.get_touch_cancel():
            break

        # SENSE: We only need the distance sensor for this robot.
        raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r = alvik.get_distance()
        closest_distance = get_closest_distance(raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r)

        # --- THINK & ACT: The State Machine ---
        
        # --- STATE 1: PATROLLING ---
        if current_state == PATROLLING:
            # Action: Drive forward with green lights
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
            alvik.set_wheels_speed(PATROL_SPEED, PATROL_SPEED)

            # Transition Check: Is there an intruder?
            if closest_distance < ALERT_DISTANCE:
                print("Intruder detected! Changing state to ALERT")
                # Stop the robot immediately
                alvik.set_wheels_speed(0, 0)
                # Change the state
                current_state = ALERT
                # IMPORTANT: Reset the spin counter every time we enter the alert state.
                spin_counter = 0

        # --- STATE 2: ALERT ---
        elif current_state == ALERT:
            # Action: Perform ONE spin and increment the counter.
            # This block will run multiple times until the counter is high enough.
            print(f"Alert! Spin #{spin_counter + 1}")
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            alvik.rotate(ALERT_SPIN_DEGREES) # Perform the alert spin
            spin_counter = spin_counter + 1

            # Transition Check: Have we spun enough times?
            if spin_counter >= ALERT_SPINS:
                print("Alert over. Changing state to PATROLLING")
                # Change the state back to patrolling
                current_state = PATROLLING
        
        sleep_ms(20)

finally:
    alvik.stop()
    print("Guard duty finished.")
