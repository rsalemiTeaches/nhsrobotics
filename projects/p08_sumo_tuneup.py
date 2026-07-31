# Project 08: Sumo Tune-Up
# GOAL: Turn your P07 survivor into a TOURNAMENT-READY fighter.
# This file is your competition program. Goal 1 is passing inspection.
# Goal 2 is being battle-ready (and adding a battle macro if you flex).

from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

# --- YOUR TUNED VALUES (WORK 1: copy your best values from P07) ---
MAX_RPM = 45
EDGE_THRESHOLD = 500

# --- STARTUP SELF-CHECK (part of inspection) ---
# Proves the sensors work before a match: prints line sensor readings
# and flashes the LEDs. The referee watches this before your first bout.
print("SELF-CHECK: line sensors =", alvik.get_line_sensors())
for _ in range(3):
    alvik.left_led.set_color(0, 1, 0)
    alvik.right_led.set_color(0, 1, 0)
    time.sleep(0.15)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    time.sleep(0.15)
print("SELF-CHECK complete. Waiting for gamepad.")

try:
    # CANCEL on the robot or OPTIONS on the gamepad ends the run.
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        # 1. SENSE
        gamepad.update()
        left_line, center_line, right_line = alvik.get_line_sensors()

        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM

        # 2. THINK
        # WORK 2: paste your working LINK-LOSS GUARD from P07 here.

        # WORK 3: paste your working EDGE GUARD from P07 here.

        # FLEX (the battle macro): pressing R1 triggers a spin attack —
        # a short pre-programmed move like your P04 functions.
        # Define a macro function above the loop and call it here:
        # if gamepad.buttons['R1']:
        #     spin_attack()

        # 3. ACT
        alvik.set_wheels_speed(left_speed, right_speed)
        time.sleep(0.02)

finally:
    alvik.set_wheels_speed(0, 0)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
