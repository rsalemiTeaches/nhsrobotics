# Project 11: Traffic Light (State Machine)
# GOAL: Learn the STATE MACHINE — the most important pattern in robotics.
#
# A state machine = the robot is always in exactly ONE state, and rules
# decide when it moves to the next state.
#
# Your robot is an intersection:
#   LEFT LED  = the North-South traffic light
#   RIGHT LED = the East-West traffic light
#   CENTER touch button = the pedestrian WALK button
#   Nano LED  = the WALK sign

from arduino_alvik import ArduinoAlvik
from nhs_robotics import NanoLED
import time

alvik = ArduinoAlvik()
alvik.begin()
nano = NanoLED()

# --- STATES (numeric constants, one per traffic situation) ---
STATE_NS_GREEN = 0
STATE_NS_YELLOW = 1
STATE_ALL_RED_1 = 2
STATE_EW_GREEN = 3
STATE_EW_YELLOW = 4
STATE_ALL_RED_2 = 5
STATE_WALK = 6

# --- TIMING (milliseconds) ---
GREEN_MS = 3000
YELLOW_MS = 1000
ALL_RED_MS = 1000
WALK_MS = 4000

current_state = STATE_NS_GREEN
state_start_time = time.ticks_ms()
walk_requested = False


def set_lights(ns_color, ew_color):
    """Helper: set both traffic lights at once. Colors are (r, g, b)."""
    alvik.left_led.set_color(*ns_color)
    alvik.right_led.set_color(*ew_color)


RED = (1, 0, 0)
YELLOW = (1, 1, 0)
GREEN = (0, 1, 0)

try:
    while not alvik.get_touch_cancel():
        now = time.ticks_ms()
        time_in_state = time.ticks_diff(now, state_start_time)

        # --- EVENTS ---
        # WORK 5 (Goal 3): if the CENTER button is touched, set
        # walk_requested = True (and light the Nano LED white so the
        # pedestrian knows the press registered).

        # --- STATE LOGIC ---
        if current_state == STATE_NS_GREEN:
            set_lights(GREEN, RED)
            # WORK 1 (Goal 1): when time_in_state > GREEN_MS, change
            # current_state to STATE_NS_YELLOW and reset
            # state_start_time to now.

        elif current_state == STATE_NS_YELLOW:
            set_lights(YELLOW, RED)
            # WORK 2 (Goal 1): after YELLOW_MS -> STATE_ALL_RED_1

        elif current_state == STATE_ALL_RED_1:
            set_lights(RED, RED)
            # WORK 6 (Goal 3): if walk_requested, go to STATE_WALK
            # instead of STATE_EW_GREEN. Otherwise:
            # WORK 3 (Goal 2): after ALL_RED_MS -> STATE_EW_GREEN

        elif current_state == STATE_EW_GREEN:
            set_lights(RED, GREEN)
            # WORK 4 (Goal 2): after GREEN_MS -> STATE_EW_YELLOW.
            # Then write the EW_YELLOW and ALL_RED_2 states below,
            # mirroring the NS side, so the cycle repeats forever.

        elif current_state == STATE_EW_YELLOW:
            set_lights(RED, YELLOW)

        elif current_state == STATE_ALL_RED_2:
            set_lights(RED, RED)

        elif current_state == STATE_WALK:
            set_lights(RED, RED)
            # WORK 7 (Goal 3): blink the Nano LED white while walking.
            # After WALK_MS: clear walk_requested, turn the Nano LED
            # off, and continue to STATE_EW_GREEN.

        time.sleep(0.01)

finally:
    set_lights((0, 0, 0), (0, 0, 0))
    nano.off()
    alvik.stop()
