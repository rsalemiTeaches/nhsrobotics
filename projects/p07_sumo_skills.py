# Project 07: Sumo Skills
# GOAL: Build your tournament sumo bot. A robot that drives off the ring
# edge loses instantly, so your code has to save you from yourself --
# and then you tune it on the real ring until it is battle-ready.
#
# You are combining things you already know:
#   P03 tank driving  +  P06 sensor override  +  a new sensor (line sensors)
#
# This file IS your competition program. Capstone 1 is the tournament.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p07.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

# --- YOUR TUNED VALUES (WORK 3) ---
# MAX_RPM: stronger pushing and faster escapes, but easier to launch
# yourself off the edge before the guard can save you. There is no
# perfect number -- there is only the number YOU can drive.
MAX_RPM = 45

# The ring floor is dark; the boundary is a white edge about 3 inches
# wide. The three line sensors read LOW numbers over the white edge and
# HIGH numbers over the dark floor.
EDGE_THRESHOLD = 500

# How often to refresh the OLED. Writing the screen every lap would slow
# the loop down, so we use the P09 clock trick to do it 5 times a second.
last_screen_time = time.ticks_ms()
SCREEN_MS = 200


# --- STARTUP SELF-CHECK (given to you -- part of inspection) ---
# Proves the sensors are alive and the program is fresh BEFORE your
# first bout. The referee watches this. It also catches the classic
# "sensor cable came loose" failure while there is still time to fix it.
print("SELF-CHECK: line sensors =", alvik.get_line_sensors())
sb.update_display("SELF-CHECK", "sensors OK", "waiting for pad")
for _ in range(3):
    alvik.left_led.set_color(0, 1, 0)
    alvik.right_led.set_color(0, 1, 0)
    time.sleep(0.15)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    time.sleep(0.15)
print("SELF-CHECK complete. Waiting for gamepad.")


# FLEX (the battle macro): define a short pre-programmed attack or
# escape move here, the same way you wrote functions in P04, then call
# it from the loop when R1 is pressed. Note the capital R1.
#
# def spin_attack():
#     ...


try:
    # CANCEL on the robot or OPTIONS on the gamepad ends the run.
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        # --- 1. SENSE ---
        gamepad.update()
        left_line, center_line, right_line = alvik.get_line_sensors()

        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM

        # --- 2. THINK ---
        # WORK 1: DETECT the edge. Build a True/False variable using the
        # 2-of-3 rule. Sort the three readings, then look at the MIDDLE
        # one: if even the middle reading is below the threshold, at
        # least TWO sensors are over white, so you are crossing out.
        #   sorted_sensors = sorted((left_line, center_line, right_line))
        #   edge_detected = sorted_sensors[1] < EDGE_THRESHOLD

        # WORK 2: ACT on it. When edge_detected is True, block FORWARD
        # driving (positive speeds only, exactly like P06) and turn the
        # LEDs red. When it is False, LEDs green. Reverse must ALWAYS
        # stay allowed -- backing away from the edge is how you survive.

        # FLEX (continued): call your battle macro here.
        # if gamepad.buttons['R1']:
        #     spin_attack()

        # --- 3. ACT ---
        alvik.set_wheels_speed(left_speed, right_speed)

        # --- TUNING READOUT (given to you) ---
        # Shows the three line sensor readings so you can tune
        # EDGE_THRESHOLD in WORK 3 with no USB cable attached. Push the
        # robot slowly from the dark floor onto the white rim, watch the
        # numbers, and pick a threshold between the two.
        if time.ticks_diff(time.ticks_ms(), last_screen_time) > SCREEN_MS:
            sb.update_display("L C R sensors",
                              "{} {} {}".format(left_line, center_line, right_line),
                              "EDGE={}".format(EDGE_THRESHOLD))
            last_screen_time = time.ticks_ms()

        time.sleep(0.02)

finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
