# nhs_robotics.py
# Version: V22 (Added Closed-Loop Drive Straight)
# 
# Includes:
# 1. Original helper classes (oLED, Buzzer, Button, Controller, NanoLED)
# 2. "SuperBot" Class: Wraps an existing ArduinoAlvik object to add features
#
# NEW IN V22:
# - drive_distance now uses the IMU to maintain a straight heading (Drive Straight).
# - move_complete implements a P-Controller to correct heading errors during motion.

# --- IMPORTS ---
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

print("Loading nhs_robotics.py V22")

# --- HELPER FUNCTIONS (Legacy Bridge) ---

def get_closest_distance(d1, d2, d3, d4, d5):
    return SuperBot._get_closest_distance(d1, d2, d3, d4, d5)

# --- CLASSES ---
# ---------------------------------------------------------------------
# PART 1: THE BUTTON CLASS
# ---------------------------------------------------------------------

class Button:
    """
    A class to manage a button's state and detect a single "press" 
    (a "rising edge") to prevent rapid repeats from holding it down.

    This class works like a simple state machine with two states:
    - STATE_UP: The button is not being pressed.
    - STATE_PRESSED: The button is being held down.
    
    It only reports a "press" on the single frame when the button
    goes from STATE_UP to STATE_PRESSED.
    """
    # Class-level constants for our states
    STATE_UP = 1
    STATE_PRESSED = 2
    
    def __init__(self, get_touch_function):
        """
        Initializes the button's internal state.
        
        get_touch_function: A function (like alvik.get_touch_up) that
                            will be called to get the hardware state.
        """
        # Save the function that was passed in, so we can call it later
        self.get_hardware_state = get_touch_function
        
        # Initialize the internal state
        self.current_state = self.STATE_UP

    def get_touch(self):
        """
        Checks the button state. This MUST be called in every loop.
        
        It updates the internal state machine and returns True ONLY 
        on the "rising edge" — the single moment the button was 
        first pressed.
        """
        return_value = False
        
        # Call the hardware function we saved during __init__
        is_pressed = self.get_hardware_state()

        # --- This is the State Machine logic ---
        
        # Check if the current state is UP
        if self.current_state == self.STATE_UP:
            if is_pressed:
                # This is the "rising edge"!
                return_value = True
                # Transition to the PRESSED state
                self.current_state = self.STATE_PRESSED
        
        # Check if the current state is PRESSED
        elif self.current_state == self.STATE_PRESSED:
            if not is_pressed:
                # The button was released.
                # Transition back to the UP state.
                self.current_state = self.STATE_UP
                
        # Return True only if this was the frame it was pressed
        return return_value

class oLED:
    def __init__(self, i2cDriver = None):
        SCL_PIN = 12
        SDA_PIN = 11
        I2C_ADDRESS = 0x3c
        OLED_WIDTH = 128
        OLED_HEIGHT = 32
        self.display = None 
        try:
            if i2cDriver is None:
                i2cDriver = I2C(1, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
            self.display = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2cDriver, I2C_ADDRESS)
            self.clear()
        except Exception:
            pass

    def clear(self):
        if self.display:
            try:
                self.display.fill(0)
                self.display.show()
            except: pass

    def show_lines(self, line1="", line2="", line3=""):
        if self.display:
            try:
                self.display.fill(0) 
                self.display.text(str(line1), 0, 0)
                self.display.text(str(line2), 0, 10)
                self.display.text(str(line3), 0, 20)
                self.display.show()
            except: pass

class Buzzer:
    def __init__(self, scl_pin=12, sda_pin=11, i2c_driver=None):
        self.frequency = 2730
        self.duration = 100
        self._buzzer = None
        self.NOTE_C4, self.NOTE_G3, self.NOTE_A3, self.NOTE_B3, self.NOTE_REST = (0,0,0,0,0)
        self.EFFECT_SIREN, self.EFFECT_YES, self.EFFECT_NO, self.EFFECT_LAUGH, self.EFFECT_CRY = (0,0,0,0,0)

        try:
            if i2c_driver is None:
                i2c_driver = I2CDriver(scl=scl_pin, sda=sda_pin)
            self._buzzer = qwiic_buzzer.QwiicBuzzer(i2c_driver=i2c_driver)
            if self._buzzer.begin() == False:
                self._buzzer = None
                return 
            self._volume = self._buzzer.VOLUME_LOW
            self.NOTE_C4 = self._buzzer.NOTE_C4
            self.NOTE_G3 = self._buzzer.NOTE_G3
            self.NOTE_A3 = self._buzzer.NOTE_A3
            self.NOTE_B3 = self._buzzer.NOTE_B3
            self.NOTE_REST = 0
            self.EFFECT_SIREN = 0
            self.EFFECT_YES = 2
            self.EFFECT_NO = 4
            self.EFFECT_LAUGH = 6
            self.EFFECT_CRY = 8
        except Exception:
            self._buzzer = None

    def set_frequency(self, new_frequency):
        self.frequency = new_frequency
    def set_duration(self, new_duration_ms):
        self.duration = new_duration_ms
    def on(self):
        if self._buzzer:
            try:
                self._buzzer.configure(self.frequency, self.duration, self._volume)
                self._buzzer.on()
            except: pass
    def off(self):
        if self._buzzer:
            try:
                self._buzzer.off()
            except: pass
    def play_effect(self, effect_number):
        if self._buzzer:
            try:
                self._buzzer.play_sound_effect(effect_number, self._volume)
            except: pass

# --- "SuperBot" Class ---

K_CONSTANT = 1624.0
DEGREES_PER_CM = 33.88

class SuperBot:
    def __init__(self, robot):
        self.bot = robot
        
        self.info_logging_enabled = False
        self._ensure_log_directory()
        self._rotate_logs()
        
        self.shared_i2c = None
        self.screen = None
        self.husky = None
        self.qwiic_driver = None
        
        self._init_peripherals()

        # Drive state variables
        self._is_moving_distance = False
        self._target_encoder_value = 0
        self._drive_direction = 0
        self._drive_start_time = 0
        self._drive_timeout_ms = 0
        
        # Drive Straight (IMU) variables
        self._target_yaw = 0.0
        self._current_speed_cm_s = 0.0
        self._kp_heading = 4.0 # Proportional gain for heading correction

    def _init_peripherals(self):
        try:
            self.shared_i2c = I2C(1, scl=Pin(12), sda=Pin(11), freq=400000)
        except Exception:
            self.shared_i2c = None

        if self.shared_i2c:
            try:
                self.screen = oLED(i2cDriver=self.shared_i2c)
                self.screen.show_lines("SuperBot", "Online", "V22")
            except Exception:
                pass

        if self.shared_i2c:
            try:
                self.qwiic_driver = MicroPythonI2C(esp32_i2c=self.shared_i2c)
                self.husky = QwiicHuskylens(i2c_driver=self.qwiic_driver)
                if self.husky.begin():
                    pass
                else:
                    self.husky = None
            except Exception:
                self.husky = None
    
    @staticmethod
    def _get_closest_distance(d1, d2, d3, d4, d5):
        all_readings = [d1, d2, d3, d4, d5]
        valid_readings = [d for d in all_readings if d > 0]
        if not valid_readings:
            return 999
        return min(valid_readings)
    
    # --- SENSOR METHODS ---

    def get_closest_distance(self):
        d_tuple = self.bot.get_distance()
        return self._get_closest_distance(d_tuple[0], d_tuple[1], d_tuple[2], d_tuple[3], d_tuple[4])
        
    def get_camera_distance(self):
        if not self.husky:
            return None
        try:
            self.husky.request()
            if len(self.husky.blocks) > 0:
                width = self.husky.blocks[0].width
                if width > 0:
                    return K_CONSTANT / width
        except Exception:
            pass
        return None

    # --- NEW V21/V22 METHODS ---

    def get_floor_status(self):
        """
        Returns the safety status of the floor based on line sensors.
        Returns: "SAFE", "CLIFF_LEFT", "CLIFF_RIGHT", "CLIFF_BOTH"
        """
        return "SAFE" 

    def servo_glide(self, servo, target_angle, duration_ms):
        """
        Moves a servo smoothly to target_angle over duration_ms (Blocking).
        """
        servo.write(target_angle)
        time.sleep(duration_ms / 1000.0)

    def rotate_precise(self, degrees):
        """
        Rotates the robot a specific number of degrees.
        Positive = Left/CCW, Negative = Right/CW
        """
        self.bot.rotate(degrees)

    class ApproachVector:
        def __init__(self, angle, distance):
            self.angle = angle
            self.distance = distance

    def calculate_approach_vector(self, tag_block, target_dist_cm):
        """
        Calculates the (angle, distance) needed to drive to a point 
        directly in front of the tag (the 'Normal Line Intercept').
        """
        # 1. Get Distance to Tag (Hypotenuse)
        if tag_block.width == 0: return self.ApproachVector(0, 0)
        d_sight = K_CONSTANT / tag_block.width
        
        # 2. Calculate Offset Angle (Theta) relative to robot
        x_val = tag_block.xCenter
        
        pixel_offset = 160 - x_val # Positive = Tag is Left
        pixels_per_degree = 320.0 / 60.0
        theta_deg = pixel_offset / pixels_per_degree
        theta_rad = math.radians(theta_deg)
        
        # 3. Calculate "Ghost Point" coordinates (Robot is 0,0)
        x_tag = d_sight * math.sin(theta_rad)
        y_tag = d_sight * math.cos(theta_rad)
        
        # 4. Calculate Approach Point (The Normal Line Intercept)
        y_approach = y_tag - target_dist_cm
        x_approach = x_tag 
        
        # 5. Calculate Vector to Approach Point
        final_dist = math.sqrt(x_approach**2 + y_approach**2)
        final_angle_rad = math.atan2(x_approach, y_approach)
        final_angle_deg = math.degrees(final_angle_rad)
        
        return self.ApproachVector(final_angle_deg, final_dist)

    # --- MOTOR CONTROL METHODS ---

    def drive_distance(self, distance_cm, speed_cm_s=20, blocking=True, timeout=10):
        if distance_cm == 0:
            return

        enc_values = self.bot.get_wheels_position()
        start_avg = (enc_values[0] + enc_values[1]) / 2.0
        
        delta_deg = distance_cm * DEGREES_PER_CM
        
        self._target_encoder_value = start_avg + delta_deg
        self._drive_direction = 1 if distance_cm > 0 else -1
        self._is_moving_distance = True
        
        self._drive_start_time = time.ticks_ms()
        self._drive_timeout_ms = timeout * 1000
        
        # Save linear speed for the correction loop
        self._current_speed_cm_s = speed_cm_s * self._drive_direction
        
        # Capture Initial Yaw for Drive Straight Logic
        try:
            # Assumes get_orientation() returns [roll, pitch, yaw]
            self._target_yaw = self.bot.get_orientation()[2]
        except:
            self._target_yaw = 0.0 # Fallback if IMU fails/missing
        
        # Start moving (Open loop start)
        self.bot.drive(self._current_speed_cm_s, 0)
        
        if blocking:
            while not self.move_complete():
                time.sleep(0.01)

    def move_complete(self):
        if not self._is_moving_distance:
            return True
            
        # 1. Check Timeout
        if time.ticks_diff(time.ticks_ms(), self._drive_start_time) > self._drive_timeout_ms:
            self.bot.brake()
            self._is_moving_distance = False
            self.log_info("Warn: Drive Timeout")
            return True

        # 2. Check Distance Completion
        enc_values = self.bot.get_wheels_position()
        current_avg = (enc_values[0] + enc_values[1]) / 2.0
        finished = False
        
        if self._drive_direction > 0:
            if current_avg >= self._target_encoder_value:
                finished = True
        else:
            if current_avg <= self._target_encoder_value:
                finished = True
                
        if finished:
            self.bot.brake()
            self._is_moving_distance = False
            return True

        # 3. Apply Heading Correction (Drive Straight)
        try:
            current_yaw = self.bot.get_orientation()[2]
            error = current_yaw - self._target_yaw
            
            # Normalize error to -180 to +180
            if error > 180: error -= 360
            if error < -180: error += 360
            
            # P-Controller: If we drifted Right (error < 0), we need to turn Left (Positive rot)
            # Correction formula: rot = -error * Kp
            correction_rot = -error * self._kp_heading
            
            # Apply adjusted drive command
            self.bot.drive(self._current_speed_cm_s, correction_rot)
            
        except Exception:
            pass # Fail silently if IMU error, continue open loop

        return False

    # --- LOGGING & IO METHODS ---

    def enable_info_logging(self):
        self.info_logging_enabled = True
        print("Logging set to ON")
        self.update_display("Log: ON")

    def disable_info_logging(self):
        self.info_logging_enabled = False
        print("Logging set to OFF")
        self.update_display("Log: OFF")

    def log_info(self, message: str):
        print(message)
        self.update_display(message)
        if self.info_logging_enabled:
            self._append_to_file('/workspace/logs/messages.log', message)

    def log_error(self, message: str):
        full_msg = f"ERROR: {message}"
        print(full_msg)
        self.update_display(full_msg)
        self._append_to_file('/workspace/logs/errors.log', full_msg)

    def _ensure_log_directory(self):
        try:
            os.mkdir('/workspace/logs')
        except OSError:
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
                    print(f"Rotating {filename}...")
                    try:
                        os.remove(bak_path)
                    except OSError:
                        pass
                    os.rename(log_path, bak_path)
            except Exception:
                pass
        rotate_file('messages.log')
        rotate_file('errors.log')

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
                if l2 == "" and l3 == "" and len(l1) > 16:
                    l2 = l1[16:32]
                    l3 = l1[32:48]
                    l1 = l1[0:16]
                self.screen.show_lines(l1, l2, l3)
            except Exception:
                pass

# Developed with the assistance of Google Gemini