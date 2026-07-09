# test_follow_line_hw.py — TEACHER HARDWARE SMOKE TEST (not for students)
# Place robot on a taped line, run, press CANCEL (X) to stop.
# Pass = robot tracks the line for 15 seconds without leaving it.
from arduino_alvik import ArduinoAlvik
from nhs_robotics import LineFollower
from time import sleep_ms, ticks_ms, ticks_diff

BASE_SPEED = 25  # start slow; raise after first clean run

alvik = ArduinoAlvik()
alvik.begin()
lf = LineFollower(alvik)
start = ticks_ms()
try:
    while not alvik.get_touch_cancel():
        sleep_ms(15)
        left, right = lf.follow(BASE_SPEED)
        if lf.line_lost:
            alvik.left_led.set_color(1, 0, 0)   # red = lost
            alvik.right_led.set_color(1, 0, 0)
            alvik.brake()
            continue
        alvik.left_led.set_color(0, 1, 0)
        alvik.right_led.set_color(0, 1, 0)
        alvik.set_wheels_speed(left, right)
        if ticks_diff(ticks_ms(), start) > 15000:
            print("15 s complete - PASS if still on line")
finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
