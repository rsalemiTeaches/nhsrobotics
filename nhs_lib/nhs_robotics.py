# nhs_robotics.py
# Version: V36
# 
# Includes:
# 1. Original helper classes (oLED, Buzzer, Button, Controller, NanoLED)
# 2. "SuperBot" Class: Wraps an existing ArduinoAlvik object to add features
#
# NEW IN V36:
# - REFACTOR: Renamed self.bot -> self.alvik for student consistency.
# - Students can now access sb.alvik.left_led, etc.

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
from controller import Controller

from qwiic_huskylens import QwiicHuskylens

print("Loading nhs_robotics.py V36")

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

class SuperBot:
    # Mode Constants (Integers)
    MODE_IDLE = 0
    MODE_DISTANCE = 1
    MODE_APRIL_TAG = 2 
    MODE_DRIVE_TO_LINE = 3 

    def __init__(self, alvik):
        self.alvik = alvik # REFACTOR: Was self.bot
        
        # --- CONSTANTS ---
        self.K_CONSTANT = 1624.0
        self.DEGREES_PER_CM = 33.88
        
        self.info_logging_enabled = False
        self._ensure_log_directory()
        self._rotate_logs()
        
        # Write Log Header Separator
        self._append_to_file('/workspace/logs/messages.log', '#' * 30)
        self._append_to_file('/workspace/logs/errors.log', '#' * 30)
        
        self.shared_i2c = None
        self.screen = None
        self.husky = None
        self.qwiic_driver = None
        
        self._init_peripherals()
        
        if self.husky:
            print(f"SuperBot Init Complete. HuskyLens is active.")
        else:
            print(f"SuperBot Init Complete. HuskyLens is NONE.")

        # --- STATE VARIABLES ---
        self._current_mode = self.MODE_IDLE
        
        # Distance Mode Variables
        self._target_encoder_value = 0
        self._drive_direction = 0
        self._drive_start_time = 0
        self._drive_timeout_ms = 0
        
        # April Tag Mode Variables
        self._vs_target_id = 1
        self._vs_stop_distance = 0
        self._vs_speed = 0
        self._vs_lost_count = 0
        self._vs_last_dist = 999.0
        
        # Drive To Line Mode Variables
        self._lf_speed = 0
        self._lf_threshold = 500
        
        # IMU Heading Correction
        self._target_yaw = 0.0
        self._current_speed_cm_s = 0.0
        self._kp_heading = 4.0 

    def _init_peripherals(self):
        try:
            self.shared_i2c = I2C(1, scl=Pin(12), sda=Pin(11), freq=400000)
        except Exception as e:
            self.shared_i2c = None
            print(f"I2C Init Error: {e}")

        if self.shared_i2c:
            try:
                self.screen = oLED(i2cDriver=self.shared_i2c)
                self.screen.show_lines("SuperBot", "Online", "V36")
            except Exception:
                pass

        if self.shared_i2c:
            try:
                self.qwiic_driver = MicroPythonI2C(esp32_i2c=self.shared_i2c)
                print("Init HuskyLens...")
                self.update_display("Init HuskyLens...", "Please Wait")
                
                attempts = 0
                success = False
                while attempts < 10 and not success:
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
                self.log_error(f"Husky Setup Error: {e}")
    
    @staticmethod
    def _get_closest_distance(d1, d2, d3, d4, d5):
        all_readings = [d1, d2, d3, d4, d5]
        valid_readings = [d for d in all_readings if d > 0]
        if not valid_readings:
            return 999
        return min(valid_readings)
    
    # --- STUDENT-FRIENDLY METHODS ---

    def align_to_tag(self, target_id=1, align_dist=25.0):
        """
        High-level method to align the robot with a tag.
        Blocking call. Returns True/False.
        """
        self.log_info("Aligning...")
        tag = None
        for _ in range(5):
            try:
                self.husky.request()
                blocks = [b for b in self.husky.blocks if b.id == target_id]
                if blocks:
                    tag = blocks[0]
                    break
            except: pass
            time.sleep(0.1)
            
        if not tag:
            self.log_error("Align Fail: No Tag")
            return False
            
        vector = self.calculate_approach_vector(tag, align_dist)
        
        self.alvik.rotate(vector.angle)
        self.drive_distance(vector.distance)
        self.alvik.rotate(-vector.angle)
        
        return self.center_on_tag(target_id=target_id)

    def approach_tag(self, target_id=1, stop_distance=8.0, speed=5, blocking=True):
        """
        Visual Servoing approach (AprilTag Mode).
        Blocking=True: Runs until done, then brakes.
        Blocking=False: Returns immediately, sets mode. Caller calls move_complete().
        """
        self.log_info(f"Approaching ID {target_id}...")
        
        # Setup state
        self._current_mode = self.MODE_APRIL_TAG
        self._vs_target_id = target_id
        self._vs_stop_distance = stop_distance
        self._vs_speed = speed # This is now interpreted as cm/s, NOT RPM
        self._vs_lost_count = 0
        self._vs_last_dist = 999.0
        
        # Start moving (Straight initially)
        self.alvik.drive(speed, 0)
        
        if blocking:
            while not self.move_complete():
                time.sleep(0.05)
            # Explicit braking because move_complete is now a pure query
            self.alvik.brake()
            return True
        
        return True

    def drive_to_line(self, speed=15, threshold=500, blocking=True):
        """
        Drives until black line.
        Blocking=True: Runs until line, then brakes.
        """
        self.log_info("Driving to Line...")
        
        self._current_mode = self.MODE_DRIVE_TO_LINE
        self._lf_speed = speed
        self._lf_threshold = threshold
        
        self.alvik.drive(speed, 0)
        
        if blocking:
            while not self.move_complete():
                time.sleep(0.01)
            # Explicit braking
            self.alvik.brake()
            return True
            
        return True

    # --- SENSOR METHODS ---

    def get_closest_distance(self):
        d_tuple = self.alvik.get_distance()
        return self._get_closest_distance(d_tuple[0], d_tuple[1], d_tuple[2], d_tuple[3], d_tuple[4])
        
    def get_camera_distance(self):
        if not self.husky:
            return None
        try:
            self.husky.request()
            if len(self.husky.blocks) > 0:
                width = self.husky.blocks[0].width
                if width > 0:
                    return self.K_CONSTANT / width
        except Exception:
            pass
        return None

    # --- CORE METHODS ---

    def get_floor_status(self):
        return "SAFE" 

    def servo_glide(self, servo, target_angle, duration_ms):
        servo.write(target_angle)
        time.sleep(duration_ms / 1000.0)

        
    def get_yaw(self):
        try:
            return self.alvik.get_orientation()[2]
        except:
            return 0.0

    def center_on_tag(self, target_id=1, tolerance=5):
        if not self.husky: return False
        
        self.husky.request()
        blocks = [b for b in self.husky.blocks if b.id == target_id]
        
        if not blocks:
            return False
            
        target = blocks[0]
        error_pixels = 160 - target.xCenter
        
        if abs(error_pixels) <= tolerance:
            return True
            
        pixels_per_degree = 320.0 / 60.0
        angle_to_turn = error_pixels / pixels_per_degree
        
        self.log_info(f"Center: {error_pixels}px -> {angle_to_turn:.1f}deg")
        self.rotate_precise(angle_to_turn)
        return True

    def adjust_distance_to_tag(self, target_id=1, target_dist_cm=10, step_ratio=1.0):
        if not self.husky: return None

        self.husky.request()
        blocks = [b for b in self.husky.blocks if b.id == target_id]
        
        if not blocks: return None
            
        target = blocks[0]
        if target.width == 0: return None
        current_dist = self.K_CONSTANT / target.width
        gap = current_dist - target_dist_cm
        
        drive_amt = gap * step_ratio
        
        if abs(gap) > 0.5:
             if abs(drive_amt) < 2.0:
                 drive_amt = gap 
        else:
             drive_amt = 0 
        
        if abs(drive_amt) > 0.1:
            self.log_info(f"Dist: {current_dist:.1f} Gap: {gap:.1f} -> Drive {drive_amt:.1f}")
            self.drive_distance(drive_amt, blocking=True)
            
        return current_dist

    class ApproachVector:
        def __init__(self, angle, distance):
            self.angle = angle
            self.distance = distance

    def calculate_approach_vector(self, tag_block, target_dist_cm):
        if tag_block.width == 0: return self.ApproachVector(0, 0)
        d_sight = self.K_CONSTANT / tag_block.width
        
        x_val = tag_block.xCenter
        pixel_offset = 160 - x_val 
        pixels_per_degree = 320.0 / 60.0
        theta_deg = pixel_offset / pixels_per_degree
        theta_rad = math.radians(theta_deg)
        
        x_tag = d_sight * math.sin(theta_rad)
        y_tag = d_sight * math.cos(theta_rad)
        
        y_approach = y_tag - target_dist_cm
        x_approach = x_tag 
        
        final_dist = math.sqrt(x_approach**2 + y_approach**2)
        final_angle_rad = math.atan2(x_approach, y_approach)
        final_angle_deg = math.degrees(final_angle_rad)
        
        return self.ApproachVector(final_angle_deg, final_dist)

    # --- MOTOR CONTROL METHODS ---

    def drive_distance(self, distance_cm, speed_cm_s=20, blocking=True, timeout=10):
        if distance_cm == 0:
            return

        self._current_mode = self.MODE_DISTANCE
        enc_values = self.alvik.get_wheels_position()
        start_avg = (enc_values[0] + enc_values[1]) / 2.0
        
        delta_deg = distance_cm * self.DEGREES_PER_CM
        
        self._target_encoder_value = start_avg + delta_deg
        self._drive_direction = 1 if distance_cm > 0 else -1
        self._is_moving_distance = True
        
        self._drive_start_time = time.ticks_ms()
        self._drive_timeout_ms = timeout * 1000
        
        # Start moving
        self.alvik.drive(speed_cm_s * self._drive_direction, 0)
        
        if blocking:
            while not self.move_complete():
                time.sleep(0.01)
            # Explicit braking
            self.alvik.brake()

    def move_complete(self):
        """
        Pure Query: Returns True if action is complete, False otherwise.
        Does NOT brake the robot (unless error).
        Resets mode to IDLE upon completion.
        """
        
        # --- MODE 1: DISTANCE ---
        if self._current_mode == self.MODE_DISTANCE:
            # Timeout Check
            if time.ticks_diff(time.ticks_ms(), self._drive_start_time) > self._drive_timeout_ms:
                self.alvik.brake() # Safety brake
                self._is_moving_distance = False
                self._current_mode = self.MODE_IDLE
                self.log_info("Warn: Drive Timeout")
                return True

            enc_values = self.alvik.get_wheels_position()
            current_avg = (enc_values[0] + enc_values[1]) / 2.0
            
            finished = False
            if self._drive_direction > 0:
                if current_avg >= self._target_encoder_value:
                    finished = True
            else:
                if current_avg <= self._target_encoder_value:
                    finished = True
                    
            if finished:
                # Do NOT brake here. Caller must brake.
                self._is_moving_distance = False
                self._current_mode = self.MODE_IDLE
                return True
                
            return False

        # --- MODE 2: APRIL TAG ---
        elif self._current_mode == self.MODE_APRIL_TAG:
            try:
                self.husky.request()
            except: 
                return False 
            
            blocks = [b for b in self.husky.blocks if b.id == self._vs_target_id]
            
            if not blocks:
                self._vs_lost_count += 1
                if self._vs_lost_count > 10: 
                    # Blind Finish Logic
                    if self._vs_last_dist < 15.0:
                        self.log_info("Tag lost (Close). Blind finish.")
                        remaining = self._vs_last_dist - self._vs_stop_distance
                        if remaining > 0:
                            # Use blocking drive for the blind finish
                            # Note: self._vs_speed is now cm/s
                            self.drive_distance(remaining, speed_cm_s=self._vs_speed, blocking=True)
                        self._current_mode = self.MODE_IDLE
                        return True
                    else:
                        self.log_error("Lost Tag (Far)")
                        self.alvik.brake() # Safety brake
                        self._current_mode = self.MODE_IDLE
                        return True
                return False 
            
            self._vs_lost_count = 0
            tag = blocks[0]
            
            if tag.width == 0: return False
            dist = self.K_CONSTANT / tag.width
            self._vs_last_dist = dist
            
            if dist <= self._vs_stop_distance:
                self._current_mode = self.MODE_IDLE
                return True
                
            # Steering Logic
            error = 160 - tag.xCenter
            turn_rate = error * 0.15 
            if turn_rate > 30: turn_rate = 30
            if turn_rate < -30: turn_rate = -30
            
            # FIXED: Use drive(linear, angular) for cm/s + deg/s
            # NOT set_wheels_speed(RPM)
            self.alvik.drive(self._vs_speed, turn_rate)
            
            return False

        # --- MODE 3: DRIVE TO LINE ---
        elif self._current_mode == self.MODE_DRIVE_TO_LINE:
            l, c, r = self.alvik.get_line_sensors()
            if l > self._lf_threshold or c > self._lf_threshold or r > self._lf_threshold:
                self._current_mode = self.MODE_IDLE
                return True
            return False

        # --- MODE: IDLE ---
        else:
            return True

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