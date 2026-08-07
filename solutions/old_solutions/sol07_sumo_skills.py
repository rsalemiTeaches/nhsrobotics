# Project 07 SOLUTION: Sumo Skills (tournament-ready reference)
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

MAX_RPM = 50           # WORK 3: competitive but still controllable
EDGE_THRESHOLD = 500   # WORK 3: tuned on the real classroom ring

SPIN_SPEED = 60

last_screen_time = time.ticks_ms()
SCREEN_MS = 200


# --- STARTUP SELF-CHECK (given; part of inspection) ---
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


def spin_attack():      # FLEX
    """Quarter-second spin to shake off an attacker."""
    alvik.set_wheels_speed(SPIN_SPEED, -SPIN_SPEED)
    time.sleep(0.25)
    alvik.set_wheels_speed(0, 0)


try:
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        # 1. SENSE
        gamepad.update()
        left_line, center_line, right_line = alvik.get_line_sensors()

        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM

        # 2. THINK
        # WORK 1 -- the 2-of-3 rule: the MIDDLE (median) reading below the
        # threshold means at least two sensors see the white boundary.
        sorted_sensors = sorted((left_line, center_line, right_line))
        edge_detected = sorted_sensors[1] < EDGE_THRESHOLD

        if edge_detected:                            # WORK 2
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            if left_speed > 0:
                left_speed = 0
            if right_speed > 0:
                right_speed = 0
        else:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)

        if gamepad.buttons['R1']:                    # FLEX
            spin_attack()

        # 3. ACT
        alvik.set_wheels_speed(left_speed, right_speed)

        # Tuning readout (given): the three readings, 5x a second.
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
