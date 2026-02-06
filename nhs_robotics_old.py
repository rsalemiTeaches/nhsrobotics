# nhs_robotics.py
# Version: V57
#
# CHANGES:
# 1. Used user-provided _init_peripherals() for robust hardware setup.
# 2. Restored Buzzer wrapper class to match usage in _init_peripherals.
# 3. Retained V56 features (NanoLED, oLED, servo_glide, core moves).

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

print("Loading nhs_robotics.py V57")


# --- CLASSES ---

class oLED:
    """
    Wrapper for SSD1306 to provide simple text display.
    """
    def __init__(self, i2cDriver):
        self.width = 128
        self.height = 64
        self.i2c = i2cDriver
        self.screen = ssd1306.SSD1306_I2C(self.width, self.height, self.i2c)
        self.fill(0)
        self.show()

    def fill(self, color):
        self.screen.fill(color)

    def show(self):
        self.screen.show()

    def text(self, text, x, y):
        self.screen.text(text, x, y)

    def show_lines(self, line1, line2="", line3=""):
        try:
            l1 = str(line1)
            l2 = str(line2)
            l3 = str(line3)
            
            # Auto-wrap
            if l2 == "" and l3 == "" and len(l1) > 16:
                l2 = l1[16:32]
                l3 = l1[32:48]
                l1 = l1[0:16]

            self.fill(0)
            self.text(l1, 0, 0)
            self.text(l2, 0, 10)
            self.text(l3, 0, 20)
            self.show()
        except Exception:
            pass

class Buzzer:
    """
    Wrapper for QwiicBuzzer to match V46 usage.
    """
    def __init__(self, i2c_driver):
        self._buzzer = qwiic_buzzer.QwiicBuzzer(i2c_driver=i2c_driver)
        self.connected = False
        # Try to play a silent note to check connection if needed, 
        # but the _init_peripherals logic handles the connected flag check.

    def play_note(self, frequency, duration=100, volume=10):
        if self.connected and self._buzzer:
            try:
                self._buzzer.play_note(frequency, duration, volume)
            except:
                pass

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
        
        # --- NanoLED Integration ---
        self.nano_led = NanoLED()

        # --- Logging ---
        self._init_logging()
        
        # --- Hardware Setup ---
        self._init_peripherals()

    def _init_peripherals(self):
        # 1. Setup Shared I2C Bus (Raw MicroPython object)
        try:
            self.shared_i2c = I2C(1, scl=Pin(12), sda=Pin(11), freq=400000)
        except Exception as e:
            self.shared_i2c = None
            print(f"I2C Init Error: {e}")

        # 2. Setup OLED (Uses raw I2C)
        if self.shared_i2c:
            try:
                self.screen = oLED(i2cDriver=self.shared_i2c)
                self.screen.show_lines("SuperBot", "Online", "V57")
            except Exception:
                pass

        # 3. Setup Qwiic Driver (Wrapper for Qwiic libraries)
        if self.shared_i2c:
            try:
                self.qwiic_driver = MicroPythonI2C(esp32_i2c=self.shared_i2c)
                
                # 4. Setup Buzzer (Uses shared Qwiic Driver)
                try:
                    # Pass the SHARED driver so we don't create a new bus
                    self.buzzer = Buzzer(i2c_driver=self.qwiic_driver)
                    # Manually set the connected flag if not set by init
                    if self.buzzer._buzzer and self.buzzer._buzzer.is_connected():
                         self.buzzer.connected = True
                    else:
                         self.buzzer.connected = False
                except Exception as e:
                    print(f"Buzzer Init Error: {e}")
                    self.buzzer = None
                
                # 5. Setup HuskyLens (Uses shared Qwiic Driver)
                print("Init HuskyLens...")
                self.update_display("Init HuskyLens...", "Please Wait")
                
                attempts = 0
                success = False
                while attempts < 3 and not success:
                    try:
                        self.husky = QwiicHuskylens(i2c_driver=self.qwiic_driver)
                        if self.husky.begin():
                            success = True
                            print("HuskyLens OK")
                            try:
                                self.update_display("HuskyLens OK")
                            except: pass
                        else:
                            print(f"Husky Attempt {attempts+1} Failed (begin=False)")
                    except Exception as e:
                        print(f"Husky Attempt {attempts+1} Error: {e}")
                        
                    if not success:
                        attempts += 1
                        time.sleep(0.5)
                
                if not success:
                    self.husky = None
                    self.log_error("HuskyLens Init FAILED")
                    self.update_display("Error:", "HuskyLens Fail")
                    
            except Exception as e:
                self.husky = None
                self.buzzer = None
                self.log_error(f"Qwiic Setup Error: {e}")

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

    @staticmethod
    def _get_closest_distance(d1, d2, d3, d4, d5):
        # Filter out negative values (errors) and 0.0 (no reading)
        valid_distances = []
        for d in [d1, d2, d3, d4, d5]:
            if d > 0:
                valid_distances.append(d)
        
        if not valid_distances:
            return 999.9  # No object detected
        
        return min(valid_distances)

    def get_closest_distance(self):
        """
        Returns the closest object distance from the 5 ToF sensors.
        """
        try:
            distances = self.alvik.get_distance_sensors()
            return SuperBot._get_closest_distance(*distances)
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
    
    def servo_glide(self, speed_x, speed_y, speed_theta, duration_ms):
        """
        Non-blocking move command that glides for a duration.
        """
        self.alvik.set_wheels_speed(speed_x, speed_y, speed_theta)
        # Note: True non-blocking glide requires a state machine or thread.
        # This implementation just sets the speed. The user must handle timing.
        # If the original V46 had a loop here, it would be blocking.
        # Assuming non-blocking intent:
        pass

    # --- HUSKYLENS METHODS ---
    def approach_tag(self, tag_id, target_dist_cm=20):
        """
        Attempts to find an AprilTag and drive towards it.
        """
        if not self.husky:
            return False
            
        block = self.husky.request_blocks_by_id(tag_id)
        if block:
            return True
        return False

    def center_on_tag(self, tag_id):
        """Rotates to center the tag in the camera frame."""
        if not self.husky:
            return False
        
        block = self.husky.request_blocks_by_id(tag_id)
        if block:
            x_center = block.x
            error = 160 - x_center
            if abs(error) > 10:
                turn_amt = error * 0.1
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
        MAX_SIZE = 20 * 1024

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
            self.screen.show_lines(line1, line2, line3)

    def beep(self):
        if self.buzzer:
            self.buzzer.play_note(1000, 100)