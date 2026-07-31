# Project 10 SOLUTION: Traffic Light (State Machine)
from arduino_alvik import ArduinoAlvik
from nhs_robotics import NanoLED
import time

alvik = ArduinoAlvik()
alvik.begin()
nano = NanoLED()

STATE_NS_GREEN = 0
STATE_NS_YELLOW = 1
STATE_ALL_RED_1 = 2
STATE_EW_GREEN = 3
STATE_EW_YELLOW = 4
STATE_ALL_RED_2 = 5
STATE_WALK = 6

GREEN_MS = 3000
YELLOW_MS = 1000
ALL_RED_MS = 1000
WALK_MS = 4000

current_state = STATE_NS_GREEN
state_start_time = time.ticks_ms()
walk_requested = False

# Walk-sign blink, using P09's pattern (NOT a modulo trick).
walk_led_on = False
walk_last_toggle = time.ticks_ms()
WALK_BLINK_MS = 250


def set_lights(ns_color, ew_color):
    alvik.left_led.set_color(*ns_color)
    alvik.right_led.set_color(*ew_color)


RED = (1, 0, 0)
YELLOW = (1, 1, 0)
GREEN = (0, 1, 0)


def go_to(state, now):
    """Helper: change state and restart the state clock."""
    global current_state, state_start_time
    current_state = state
    state_start_time = now


try:
    while not alvik.get_touch_cancel():
        now = time.ticks_ms()
        time_in_state = time.ticks_diff(now, state_start_time)

        # EVENTS (WORK 3)
        if alvik.get_touch_center() and not walk_requested:
            walk_requested = True
            nano.set_rgb(255, 255, 255)
            print("Walk requested.")

        # STATE LOGIC
        if current_state == STATE_NS_GREEN:
            set_lights(GREEN, RED)
            if time_in_state > GREEN_MS:              # WORK 1
                go_to(STATE_NS_YELLOW, now)

        elif current_state == STATE_NS_YELLOW:
            set_lights(YELLOW, RED)
            if time_in_state > YELLOW_MS:             # WORK 1 (continued)
                go_to(STATE_ALL_RED_1, now)

        elif current_state == STATE_ALL_RED_1:
            set_lights(RED, RED)
            if time_in_state > ALL_RED_MS:
                if walk_requested:                    # WORK 3 (continued)
                    go_to(STATE_WALK, now)
                else:                                 # WORK 2
                    go_to(STATE_EW_GREEN, now)

        elif current_state == STATE_EW_GREEN:
            set_lights(RED, GREEN)
            if time_in_state > GREEN_MS:              # WORK 2 (continued)
                go_to(STATE_EW_YELLOW, now)

        elif current_state == STATE_EW_YELLOW:
            set_lights(RED, YELLOW)
            if time_in_state > YELLOW_MS:
                go_to(STATE_ALL_RED_2, now)

        elif current_state == STATE_ALL_RED_2:
            set_lights(RED, RED)
            if time_in_state > ALL_RED_MS:
                go_to(STATE_NS_GREEN, now)

        elif current_state == STATE_WALK:
            set_lights(RED, RED)
            # WORK 3 (continued): blink the walk sign, P09 style
            if time.ticks_diff(now, walk_last_toggle) > WALK_BLINK_MS:
                walk_led_on = not walk_led_on
                if walk_led_on:
                    nano.set_rgb(255, 255, 255)
                else:
                    nano.off()
                walk_last_toggle = now
            if time_in_state > WALK_MS:
                walk_requested = False
                nano.off()
                go_to(STATE_EW_GREEN, now)

        # FLEX (night mode): hold UP to enter a FLASHING_WARN state —
        # both lights blink yellow until UP is pressed again.

        time.sleep(0.01)
finally:
    set_lights((0, 0, 0), (0, 0, 0))
    nano.off()
    alvik.stop()
