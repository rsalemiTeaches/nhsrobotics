# nhs_robotics.py
# Version: V15 (Final: SuperBot Composition + Logging Rename)
# 
# Includes:
# 1. Original helper classes (oLED, Buzzer, Button, Controller, NanoLED)
# 2. "SuperBot" Class: Wraps an existing ArduinoAlvik object to add features
#    (Fixes singleton/hang issues by using Composition instead of Inheritance)
# 3. Full backward compatibility with previous student code

# --- IMPORTS ---
import qwiic_buzzer
from qwiic_i2c.micropython_i2c import MicroPythonI2C as I2CDriver # Alias for compatibility
from qwiic_i2c.micropython_i2c import MicroPythonI2C # Explicit import for SuperBot
from nanolib import NanoLED
from button import Button
from controller import Controller
import ssd1306
from machine import Pin, I2C
import time
import os
import sys

# Import for SuperBot
from arduino_alvik import ArduinoAlvik
from qwiic_huskylens import QwiicHuskylens

print("Loading nhs_robotics.py V15")

# --- HELPER FUNCTIONS (Legacy Bridge) ---

def get_closest_distance(d1, d2, d3, d4, d5):
    """
    Finds the minimum valid distance from the five ToF sensor zones.
    A valid reading is any positive number.
    
    BRIDGE: This now calls the static method in SuperBot to ensure logic is shared.
    """
    return SuperBot._get_closest_distance(d1, d2, d3, d4, d5)

# --- CLASSES ---

class oLED:
    """
    A simplified interface for the 128x32 I2C OLED display.
    """
    def __init__(self, i2cDriver = None):
        # Configuration is hardcoded here so students don't need it.
        SCL_PIN = 12
        SDA_PIN = 11
        I2C_ADDRESS = 0x3c
        OLED_WIDTH = 128
        OLED_HEIGHT = 32
        
        self.display = None 
        
        try:
            # Create a native MicroPython I2C object if one wasn't passed.
            if i2cDriver is None:
                # Use Hardware I2C (ID=1) to avoid deprecation warning
                i2cDriver = I2C(1, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
            
            # Initialize the OLED display driver
            self.display = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2cDriver, I2C_ADDRESS)
            self.clear()
            # print("OLED display initialized successfully.") # Optional: Commented out for silence

        except Exception:
            # Fail silently to allow operation without screen
            pass

    def clear(self):
        """Clears the entire screen."""
        if self.display:
            try:
                self.display.fill(0)
                self.display.show()
            except: pass

    def show_lines(self, line1="", line2="", line3=""):
        """
        The easiest way to display text. Clears the screen and shows up to
        three lines of text at once.
        """
        if self.display:
            try:
                self.display.fill(0) 
                self.display.text(str(line1), 0, 0)
                self.display.text(str(line2), 0, 10)
                self.display.text(str(line3), 0, 20)
                self.display.show()
            except: pass


class Buzzer:
    """
    A simplified interface for the SparkFun Qwiic Buzzer.
    Updated to accept an optional i2c_driver for shared bus usage.
    """
    def __init__(self, scl_pin=12, sda_pin=11, i2c_driver=None):
        """
        Initializes the connection to the buzzer.
        """
        self.frequency = 2730
        self.duration = 100
        self._buzzer = None
        
        # Initialize constants to 0 to avoid errors if buzzer fails
        self.NOTE_C4, self.NOTE_G3, self.NOTE_A3, self.NOTE_B3, self.NOTE_REST = (0,0,0,0,0)
        self.EFFECT_SIREN, self.EFFECT_YES, self.EFFECT_NO, self.EFFECT_LAUGH, self.EFFECT_CRY = (0,0,0,0,0)

        try:
            # Backward compatibility: Create driver if none provided
            if i2c_driver is None:
                i2c_driver = I2CDriver(scl=scl_pin, sda=sda_pin)
                
            self._buzzer = qwiic_buzzer.QwiicBuzzer(i2c_driver=i2c_driver)

            if self._buzzer.begin() == False:
                # Fail silently/gracefully
                self._buzzer = None
                return 
            
            self._volume = self._buzzer.VOLUME_LOW
            
            # Map constants from the driver
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
        """Sets the frequency (pitch) of the tone in Hertz (Hz)."""
        self.frequency = new_frequency

    def set_duration(self, new_duration_ms):
        """Sets how long the buzz will last in milliseconds."""
        self.duration = new_duration_ms

    def on(self):
        """Turns the buzzer on with the currently set frequency and duration."""
        if self._buzzer:
            try:
                self._buzzer.configure(self.frequency, self.duration, self._volume)
                self._buzzer.on()
            except: pass

    def off(self):
        """Immediately turns the buzzer off."""
        if self._buzzer:
            try:
                self._buzzer.off()
            except: pass

    def play_effect(self, effect_number):
        """Plays a pre-programmed sound effect."""
        if self._buzzer:
            try:
                self._buzzer.play_sound_effect(effect_number, self._volume)
            except: pass


# --- "SuperBot" Class (Composition Pattern) ---

# Constants for SuperBot
K_CONSTANT = 1624.0 # For distance calculation (Width * Distance)

class SuperBot:
    """
    The 'SuperBot' upgrade for the Alvik.
    This class wraps an existing ArduinoAlvik object to add capabilities
    like Logging, Screen management, and Vision, without interfering 
    with the robot's internal drivers.
    
    Usage:
      robot = ArduinoAlvik()
      robot.begin()
      bot = SuperBot(robot)
      bot.log_info("Ready")
    """
    def __init__(self, robot):
        self.bot = robot # Use 'bot' as the attribute name per user request
        
        # 1. Setup Logging System
        self.info_logging_enabled = False # Renamed per V15
        self._ensure_log_directory()
        self._rotate_logs() # Clean up old logs on boot
        
        # 2. Initialize Shared I2C Bus & Sensors
        # Since robot.begin() should already be called before creating SuperBot,
        # we can safely initialize sensors now.
        self.shared_i2c = None
        self.screen = None
        self.husky = None
        self.qwiic_driver = None
        
        self._init_peripherals()

    def _init_peripherals(self):
        """Internal method to setup I2C, OLED, and HuskyLens."""
        # Initialize Shared I2C Bus (Port 1, Pins 11/12)
        try:
            self.shared_i2c = I2C(1, scl=Pin(12), sda=Pin(11), freq=400000)
        except Exception:
            self.shared_i2c = None

        # Initialize OLED Display
        if self.shared_i2c:
            try:
                self.screen = oLED(i2cDriver=self.shared_i2c)
                self.screen.show_lines("SuperBot", "Online", "V15")
            except Exception:
                pass

        # Initialize HuskyLens
        if self.shared_i2c:
            try:
                self.qwiic_driver = MicroPythonI2C(esp32_i2c=self.shared_i2c)
                self.husky = QwiicHuskylens(i2c_driver=self.qwiic_driver)
                
                if self.husky.begin():
                    pass # Success
                else:
                    self.husky = None
            except Exception:
                self.husky = None
    
    # --- STATIC HELPERS (Bridge) ---
    
    @staticmethod
    def _get_closest_distance(d1, d2, d3, d4, d5):
        """
        Static implementation of distance logic.
        """
        all_readings = [d1, d2, d3, d4, d5]
        valid_readings = [d for d in all_readings if d > 0]
        if not valid_readings:
            return 999
        return min(valid_readings)

    # --- SENSOR METHODS ---

    def get_closest_distance(self):
        """
        Get the closest distance from the WRAPPED robot's sensors.
        """
        d_tuple = self.bot.get_distance() # Calls the wrapped object via .bot
        return self._get_closest_distance(d_tuple[0], d_tuple[1], d_tuple[2], d_tuple[3], d_tuple[4])
        
    def get_camera_distance(self):
        """
        Calculates distance to an AprilTag/Object using the K constant.
        Returns: Distance in cm (float) or None if nothing seen.
        """
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

    # --- LOGGING & IO METHODS ---

    def enable_info_logging(self): # Renamed V15
        """Enable logging non-critical messages to file."""
        self.info_logging_enabled = True
        print("Logging set to ON")
        self.update_display("Log: ON")

    def disable_info_logging(self): # Renamed V15
        """Disable logging non-critical messages to file."""
        self.info_logging_enabled = False
        print("Logging set to OFF")
        self.update_display("Log: OFF")

    def log_info(self, message: str): # Renamed V15
        """
        Standard log:
        - Always prints to console.
        - Updates Display (wrapping text across lines).
        - Writes to file ONLY if logging is enabled.
        """
        print(message)
        self.update_display(message)
        
        if self.info_logging_enabled:
            self._append_to_file('/logs/messages.log', message)

    def log_error(self, message: str):
        """
        Critical log:
        - Always prints to console.
        - Updates Display (wrapping text across lines).
        - ALWAYS writes to file (errors.log).
        """
        full_msg = f"ERROR: {message}"
        print(full_msg)
        self.update_display(full_msg)
        self._append_to_file('/logs/errors.log', full_msg)

    def _ensure_log_directory(self):
        """Creates /logs directory if it doesn't exist."""
        try:
            os.mkdir('/logs')
        except OSError:
            pass

    def _rotate_logs(self):
        """
        Checks size of messages.log. 
        If > 20KB, renames it to messages.bak (overwriting old backup).
        """
        MAX_SIZE = 20 * 1024 # 20KB limit
        try:
            log_path = '/logs/messages.log'
            bak_path = '/logs/messages.bak'
            
            try:
                stat = os.stat(log_path)
                size = stat[6] # Size is index 6
            except OSError:
                return # File doesn't exist, nothing to rotate

            if size > MAX_SIZE:
                print("Rotating logs...")
                # Remove old backup if it exists
                try:
                    os.remove(bak_path)
                except OSError:
                    pass
                
                # Rename current to backup
                os.rename(log_path, bak_path)
        except Exception:
            pass # Fail silently on FS errors

    def _append_to_file(self, filename, text):
        """Internal helper to safely write to flash memory."""
        try:
            timestamp = time.ticks_ms() / 1000.0
            with open(filename, 'a') as f:
                f.write(f"[{timestamp:.2f}] {text}\n")
        except Exception:
            # Never crash the robot because of a logging failure
            pass

    # --- HARDWARE HELPERS ---

    def update_display(self, line1, line2="", line3=""):
        """
        Safe wrapper for the OLED screen.
        If ONLY line1 is provided, it attempts to wrap it across lines 2 and 3.
        """
        if self.screen:
            try:
                l1 = str(line1)
                l2 = str(line2)
                l3 = str(line3)
                
                # Auto-wrap logic: If user sends one long string (l2/l3 empty), split it
                if l2 == "" and l3 == "" and len(l1) > 16:
                    # Basic wrap: 16 chars per line approx
                    l2 = l1[16:32]
                    l3 = l1[32:48] # Truncate after 48 chars total
                    l1 = l1[0:16]
                
                self.screen.show_lines(l1, l2, l3)
            except Exception:
                pass # Screen might have disconnected
            