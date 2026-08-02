from machine import Pin, I2C
from qwiic_i2c.micropython_i2c import MicroPythonI2C
import time

from .peripherals import Button, NanoLED
from .ui import RobotUI
from .vision import RobotVision
from .navigation import RobotNavigation
from .line_follower import LineFollower

# What get_closest_distance() reports when no sensor gives a usable
# reading. Deliberately larger than any real measurement, so code that
# asks "is something close?" says no.
NO_READING_CM = 999


class SuperBot:

    # The robot's own touch pads. Same names, same two methods, as
    # RobotGamepad.held() and RobotGamepad.pressed().
    TOUCH_NAMES = ('up', 'down', 'left', 'right', 'ok', 'cancel')

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

        # Same six, reachable by name so students write sb.pressed('ok').
        self._touch = {
            'up': self.btn_up,
            'down': self.btn_down,
            'left': self.btn_left,
            'right': self.btn_right,
            'ok': self.btn_ok,
            'cancel': self.btn_cancel,
        }
        self._touch_state = {
            'up': self.alvik.get_touch_up,
            'down': self.alvik.get_touch_down,
            'left': self.alvik.get_touch_left,
            'right': self.alvik.get_touch_right,
            'ok': self.alvik.get_touch_ok,
            'cancel': self.alvik.get_touch_cancel,
        }

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
    def closest_valid(readings):
        """The smallest usable number out of however many you hand in.

        A sensor reads None before its first packet arrives, and 0 or a
        negative number when nothing echoed back. Both mean "no answer,"
        not "something is touching me," so both get dropped. If nothing
        usable is left, the answer is NO_READING_CM -- far away, which is
        the safe thing to believe.

        Separate from get_closest_distance() so it can be tested with no
        robot attached.
        """
        valid = [reading for reading in readings
                 if reading is not None and reading > 0]
        if not valid:
            return NO_READING_CM
        return min(valid)

    def get_closest_distance(self):
        """Distance in cm to the nearest thing in front of the robot."""
        return self.closest_valid(self.alvik.get_distance())

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

    def _check(self, name):
        if name not in self._touch:
            raise ValueError(
                "No touch button named '%s'. Valid names: %s"
                % (name, ", ".join(self.TOUCH_NAMES)))

    def held(self, name):
        """True the whole time the touch pad is being touched."""
        self._check(name)
        return bool(self._touch_state[name]())

    def pressed(self, name):
        """True only at the instant the touch pad is first touched.

        One touch gives one True, however long you hold it.
        """
        self._check(name)
        return self._touch[name].is_pressed()

    def light_both_leds(self, red, green, blue):
        """Set the left and right lights to the same color.

        One call instead of two. Each of red, green, blue is 0 or 1.
        """
        self.alvik.left_led.set_color(red, green, blue)
        self.alvik.right_led.set_color(red, green, blue)

    def log_info(self, *args, sep=' '):
        """Print a message and show it on the OLED.

        Passthrough to self.ui.log_info(). PROVISIONAL: added for P03 so
        students write sb.log_info(...) instead of sb.ui.log_info(...).
        Revisit when SuperBot gets reworked.
        """
        self.ui.log_info(*args, sep=sep)

    def update_display(self, line1, line2="", line3=""):
        """Write up to three lines to the OLED.

        Passthrough to self.ui.update_display(). The screen is 128x32,
        three lines of about 16 characters each.
        """
        self.ui.update_display(line1, line2, line3)

print("Loaded superbot.py V03")
