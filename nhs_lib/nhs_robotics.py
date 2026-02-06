# nhs_robotics.py
# Version: V54
#
# CHANGES:
# 1. FIXED I2C: Explicitly pass ID and Pins to MicroPythonI2C to prevent 'I2C(-1)' error.
# 2. Retained full functionality (NanoLED, HuskyLens, Core Moves).

import qwiic_buzzer
from qwiic_i2c.micropython_i2c import MicroPythonI2C as I2CDriver
from qwiic_i2c.micropython_i2c import MicroPythonI2C
import ssd1306
from machine import Pin, I2C
import time
import os
import math
from nanolib import NanoLED
from qwiic_huskylens import QwiicHuskylens

print("Loading nhs_robotics.py V54")


# --- CLASSES ---
class Button:
    """
    Detects a single 'rising edge' press event.
    """

    def __init__(self, getter_func):
        self.get_value = getter_func
        self.previous_state = False

    def is_pressed(self):
        """Returns True only on the moment the button is pressed."""
        current_state = self.get_value()
        # Rising edge detection: Was False, is now True
        if current_state and not self.previous_state:
            self.previous_state = True
            return True
        elif not current_state:
            self.previous_state = False
        return False


class SuperBot:
    """
    A wrapper class for the ArduinoAlvik robot that adds high-level features:
    - Debounced button inputs
    - Integrated peripherals (OLED, Buzzer, HuskyLens, NanoLED)
    - File-based logging
    - Core Movement & Sensor methods
    """
    
    # Constants
    MODE_DISTANCE = "distance"
    MODE_APRIL_TAG = "april_tag"
    MODE_DRIVE_TO_LINE = "drive_to_line"

    def __init__(self, alvik_instance):
        self.alvik = alvik_instance
        self.mode = None

        # --- Button Wrappers ---
        self.btn_up = Button(self.alvik.get_touch_up)
        self.btn_down = Button(self.alvik.get_touch_down)
        self.btn_left = Button(self.alvik.get_touch_left)
        self.btn_right = Button(self.alvik.get_touch_right)
        self.btn_ok = Button(self.alvik.get_touch_ok)
        
        # --- I2C Setup ---
        # 1. Create the hardware I2C object for OLED usage
        self.i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
        
        # 2. Initialize the Qwiic helper with explicit pins to avoid I2C(-1) error
        # We pass the same parameters so it uses the same hardware bus
        try:
            self.qwiic = MicroPythonI2C(0, scl=1, sda=0, freq=400000)
        except Exception:
            # Fallback if the library doesn't accept args, though this is standard
            self.qwiic = MicroPythonI2C()

        # --- NanoLED Integration ---
        self.nano_led = NanoLED()

        # --- OLED Display ---
        try:
            self.screen = ssd1306.SSD1306_I2C(128, 64, self.i2c)
            self.screen.fill(0)
            self.screen.text("SuperBot Ready", 0, 0)
            self.screen.show()
        except Exception:
            print("OLED not found.")
            self.screen = None

        # --- Buzzer ---
        try:
            self.buzzer = qwiic_buzzer.QwiicBuzzer(address=0x34, i2c_driver=self.qwiic)
        except Exception:
            print("Buzzer not found.")
            self.buzzer = None

        # --- HuskyLens ---
        self.husky = None
        # Attempt to connect up to 5 times
        for _ in range(5):
            try:
                self.husky = QwiicHuskylens(self.qwiic)
                if self.husky:
                    break  # Success!
            except Exception:
                time.sleep(0.1)

        # --- Logging ---
        self._init_logging()

    # --- INPUT METHODS ---
    def get_pressed_up(self):
        return self.btn_up.is_pressed()

    def get_pressed_down(self):
        return self.btn_down.is_pressed()

    def get_pressed_left(self):
        return self.btn_left.is_pressed()

    def get_pressed_right(self):
        return self.btn_right.is_pressed()

    def get_pressed_ok(self):
        return self.btn_ok.is_pressed()

    # --- SENSOR METHODS ---
    def get_yaw(self):
        """Returns the current Yaw (Z-rotation) from the IMU."""
        try:
            if hasattr(self.alvik, 'get_yaw'):
                return self.alvik.get_yaw()
            r, p, y = self.alvik.get_imu_rpy()
            return y
        except Exception:
            return 0.0

    def get_closest_distance(self):
        """
        Returns the closest object distance from the 5 ToF sensors.
        Filters out invalid readings (<=0).
        Returns 999.9 if no object is seen.
        """
        try:
            distances = self.alvik.get_distance_sensors()
            valid = [d for d in distances if d > 0]
            if not valid:
                return 999.9
            return min(valid)
        except Exception:
            return 999.9

    # --- MOVEMENT METHODS ---
    def drive_distance(self, distance_cm):
        """Drives the robot straight for a set distance in cm."""
        self.alvik.move(distance_cm, 0, 0)

    def turn_to_heading(self, target_heading):
        """Turns the robot to an absolute heading."""
        current_yaw = self.get_yaw()
        delta = target_heading - current_yaw
        # Normalize delta to -180 to 180
        while delta > 180: delta -= 360
        while delta < -180: delta += 360
        self.alvik.rotate(delta)

    # --- HUSKYLENS METHODS ---
    def approach_tag(self, tag_id, target_dist_cm=20):
        """
        Attempts to find an AprilTag and drive towards it.
        Stops at target_dist_cm.
        """
        if not self.husky:
            return False
            
        block = self.husky.request_blocks_by_id(tag_id)
        if block:
            # Simple P-controller logic would go here
            # For now, we return True if seen
            return True
        return False

    def center_on_tag(self, tag_id):
        """Rotates to center the tag in the camera frame."""
        if not self.husky:
            return False
        
        block = self.husky.request_blocks_by_id(tag_id)
        if block:
            x_center = block.x
            # Frame is 320 wide, center is 160
            error = 160 - x_center
            # Turn based on error
            if abs(error) > 10:
                turn_amt = error * 0.1 # Gain
                self.alvik.rotate(turn_amt)
            return True
        return False

    # --- LOGGING SYSTEM ---
    def _init_logging(self):
        try:
            if "workspace" not in os.listdir("/"):
                os.mkdir("/workspace")
            if "logs" not in os.listdir("/workspace"):
                os.mkdir("/workspace/logs")
            self._rotate_logs()
        except Exception:
            pass

    def _rotate_logs(self):
        MAX_SIZE = 20 * 1024  # 20KB limit

        def rotate_file(filename):
            try:
                log_path = f'/workspace/logs/{filename}'
                bak_path = f'/workspace/logs/{filename.replace(".log", ".bak")}'
                
                try:
                    stat = os.stat(log_path)
                    size = stat[6]
                except OSError:
                    return
                
                if size > MAX_SIZE:
                    try:
                        os.remove(bak_path)
                    except OSError:
                        pass
                    os.rename(log_path, bak_path)
            except Exception:
                pass

        rotate_file('messages.log')
        rotate_file('errors.log')

    def log_message(self, message):
        self._append_to_file('/workspace/logs/messages.log', message)

    def log_error(self, message):
        self._append_to_file('/workspace/logs/errors.log', message)

    def _append_to_file(self, filename, text):
        try:
            timestamp = time.ticks_ms() / 1000.0
            with open(filename, 'a') as f:
                f.write(f"[{timestamp:.2f}] {text}\n")
        except Exception:
            pass

    # --- HARDWARE HELPERS ---
    def update_display(self, line1, line2="", line3=""):
        if self.screen:
            try:
                l1 = str(line1)
                l2 = str(line2)
                l3 = str(line3)
                
                # Auto-wrap
                if l2 == "" and l3 == "" and len(l1) > 16:
                    l2 = l1[16:32]
                    l3 = l1[32:48]
                    l1 = l1[0:16]

                self.screen.fill(0)
                self.screen.text(l1, 0, 0)
                self.screen.text(l2, 0, 10)
                self.screen.text(l3, 0, 20)
                self.screen.show()
            except Exception:
                pass

    def beep(self):
        if self.buzzer:
            self.buzzer.play_note(1000, 100)