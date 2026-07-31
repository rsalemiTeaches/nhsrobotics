# Project 10: Traffic Light (State Machine)
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
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p10.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

# FLEX (the A+): night mode. Holding UP enters a new FLASHING_WARN state where
# both directions blink yellow, until UP is pressed again. Copy your code into
# the FLEX box.

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


def go_to(state, now):
    """Helper: change state AND restart the state clock.

    Use this for EVERY state change. Doing it by hand means two lines
    every time, and forgetting the second one breaks the machine in a
    way that is miserable to debug.

    'global' tells Python not to make a private local copy, but to reach
    out and change the ONE current_state and state_start_time that live
    at the top level of this file. You need it whenever a function
    ASSIGNS to an outside variable. set_lights() above only READS RED,
    YELLOW and GREEN, so it does not need it.
    """
    global current_state, state_start_time
    current_state = state
    state_start_time = now


RED = (1, 0, 0)
YELLOW = (1, 1, 0)
GREEN = (0, 1, 0)

try:
    while not alvik.get_touch_cancel():
        now = time.ticks_ms()
        time_in_state = time.ticks_diff(now, state_start_time)

        # --- EVENTS ---
        # WORK 3: if the CENTER button is touched, set
        # walk_requested = True (and light the Nano LED white so the
        # pedestrian knows the press registered).

        # --- STATE LOGIC ---
        if current_state == STATE_NS_GREEN:
            set_lights(GREEN, RED)
            # WORK 1: when time_in_state > GREEN_MS, use the
            # helper:  go_to(STATE_NS_YELLOW, now)

        elif current_state == STATE_NS_YELLOW:
            set_lights(YELLOW, RED)
            # WORK 1 (continued): after YELLOW_MS -> STATE_ALL_RED_1

        elif current_state == STATE_ALL_RED_1:
            set_lights(RED, RED)
            # WORK 3 (continued): if walk_requested, go to STATE_WALK
            # instead of STATE_EW_GREEN. Otherwise:
            # WORK 2: after ALL_RED_MS -> STATE_EW_GREEN

        elif current_state == STATE_EW_GREEN:
            set_lights(RED, GREEN)
            # WORK 2 (continued): after GREEN_MS -> STATE_EW_YELLOW.
            # The EW_YELLOW and ALL_RED_2 branches below already have
            # their lights set -- add the transitions that LEAVE them,
            # mirroring the NS side, so the cycle repeats forever.

        elif current_state == STATE_EW_YELLOW:
            set_lights(RED, YELLOW)
            # WORK 2 (continued): after YELLOW_MS -> STATE_ALL_RED_2

        elif current_state == STATE_ALL_RED_2:
            set_lights(RED, RED)
            # WORK 2 (continued): after ALL_RED_MS -> back to
            # STATE_NS_GREEN, closing the cycle.

        elif current_state == STATE_WALK:
            set_lights(RED, RED)
            # WORK 3 (continued): blink the Nano LED white while
            # walking, using the P09 last_toggle_time pattern (NOT
            # sleep). After WALK_MS: clear walk_requested, turn the Nano
            # LED off, and go_to(STATE_EW_GREEN, now).

        time.sleep(0.01)

finally:
    set_lights((0, 0, 0), (0, 0, 0))
    nano.off()
    alvik.stop()
