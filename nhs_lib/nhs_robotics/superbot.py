from machine import Pin, I2C
from qwiic_i2c.micropython_i2c import MicroPythonI2C
import time

from .peripherals import Button, NanoLED
from .ui import RobotUI
from .vision import RobotVision
from .navigation import RobotNavigation
from .line_follower import LineFollower

class SuperBot:
    def __init__(self, alvik):
        self.alvik = alvik

        # --- NANO LED SETUP ---
        self.nano_led = NanoLED()

        # --- BUTTON INITIALIZATION ---
        self.btn_up = Button(self.alvik.get_touch_up)
        self.btn_down = Button(self.alvik.get_touch_down)
        self.btn_left = Button(self.alvik.get_touch_left)
        self.btn_right = Button(self.alvik.get_touch_right)
        self.btn_ok = Button(self.alvik.get_touch_ok)
        self.btn_cancel = Button(self.alvik.get_touch_cancel)

        # 1. Setup Shared I2C Bus (Raw MicroPython object)
        try:
            self.shared_i2c = I2C(1, scl=Pin(12), sda=Pin(11), freq=400000)
        except Exception as e:
            self.shared_i2c = None
            print(f"I2C Init Error: {e}")

        # 2. Setup Qwiic Driver
        self.qwiic_driver = None
        if self.shared_i2c:
            try:
                self.qwiic_driver = MicroPythonI2C(esp32_i2c=self.shared_i2c)
            except Exception as e:
                print(f"Qwiic Driver Init Error: {e}")

        # --- INITIALIZE SUBMODULES ---
        self.ui = RobotUI(self.shared_i2c, self.qwiic_driver)
        self.nav = RobotNavigation(self.alvik, self.ui)
        self.vision = RobotVision(self.qwiic_driver, self.ui, self.nav)
        self.line = LineFollower(self.alvik)

        print("SuperBot Init Complete.")

    @staticmethod
    def get_closest_distance_static(d1, d2, d3, d4, d5):
        all_readings = [d1, d2, d3, d4, d5]
        valid_readings = [d for d in all_readings if d > 0]
        if not valid_readings:
            return 999
        return min(valid_readings)

    def get_closest_distance(self):
        d_tuple = self.alvik.get_distance()
        return self.get_closest_distance_static(
            d_tuple[0], d_tuple[1], d_tuple[2], d_tuple[3], d_tuple[4]
        )

    def get_yaw(self):
        try:
            return self.alvik.get_orientation()[2]
        except Exception:
            return 0.0

    def turn_to_heading(self, target_angle, tolerance=2.0, timeout=5):
        self.nav.turn_to_heading(target_angle, self.get_yaw, tolerance, timeout)

    def follow_line(self, base_speed):
        return self.line.follow(base_speed)

    @property
    def line_lost(self):
        return self.line.line_lost

    def reset_line(self):
        self.line.reset()

    def update_display(self, line1, line2="", line3=""):
        """Write up to three lines to the OLED.

        Passthrough to self.ui.update_display(). The screen is 128x32,
        three lines of about 16 characters each.
        """
        self.ui.update_display(line1, line2, line3)

print("Loaded superbot.py V03")
