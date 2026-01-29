# nhs_robotics.py
# Version: V44
# 
# Includes:
# 1. Original helper classes (oLED, Buzzer, Button, Controller, NanoLED)
# 2. "SuperBot" Class: Wraps an existing ArduinoAlvik object
#
# NEW IN V44:
# - FIXED: Unified I2C initialization using a single shared MicroPythonI2C instance.
# - FIXED: Removed redundant I2C calls in sub-components to prevent bus lock/timeout.
# - RETAINED: All 6 debounced button methods for rising-edge detection.

import qwiic_buzzer
from qwiic_i2c.micropython_i2c import MicroPythonI2C as I2CDriver
import time
import ssd1306
from machine import Pin
from nanolib import NanoLED
from controller import Controller
from qwiic_huskylens import QwiicHuskylens

class Button:
    """Detects a single 'rising edge' press event."""
    def __init__(self, getter_func):
        self.get_value = getter_func
        self.previous_state = False

    def is_pressed(self):
        """Returns True only on the moment the button is first touched."""
        current_state = self.get_value()
        pressed = False
        if current_state and not self.previous_state:
            pressed = True
        self.previous_state = current_state
        return pressed

class Buzzer:
    """Simplified control for the Qwiic Buzzer using shared I2C driver."""
    EFFECT_SIREN = 0
    EFFECT_YES = 1
    EFFECT_NO = 2
    
    def __init__(self, i2c_driver=None, address=0x34):
        self.connected = False
        if i2c_driver is None:
            return
            
        try:
            # Passes the shared driver instance directly to the buzzer library
            self.buzzer = qwiic_buzzer.QwiicBuzzer(address, i2c_driver=i2c_driver)
            if hasattr(self.buzzer, 'begin'):
                self.connected = self.buzzer.begin()
            else:
                self.connected = self.buzzer.is_connected()
        except Exception:
            self.connected = False

    def on(self):
        if self.connected: self.buzzer.on()

    def off(self):
        if self.connected: self.buzzer.off()

    def play_effect(self, effect_number):
        if self.connected and 0 <= effect_number <= 9:
            self.buzzer.play_sound(effect_number)

class oLED:
    """Helper for the SSD1306 display using shared I2C driver."""
    def __init__(self, i2c_driver=None, width=128, height=64):
        self.display = None
        if i2c_driver is None:
            return
            
        try:
            # ssd1306 uses the provided I2C object for communication
            self.display = ssd1306.SSD1306_I2C(width, height, i2c_driver)
            self.clear()
        except Exception as e:
            print(f"OLED Init Warning: {e}")
            self.display = None

    def clear(self):
        if self.display:
            try:
                self.display.fill(0)
                self.display.show()
            except: pass

    def show_lines(self, line1, line2="", line3=""):
        if self.display:
            try:
                self.display.fill(0)
                self.display.text(str(line1), 0, 0)
                self.display.text(str(line2), 0, 20)
                self.display.text(str(line3), 0, 40)
                self.display.show()
            except: pass

class SuperBot:
    """The NHS primary robot interface."""
    def __init__(self, alvik_instance):
        self.alvik = alvik_instance
        
        # Initialize Shared I2C Driver ONCE per robot session
        # Pins 13 (SCL) and 12 (SDA) are standard for the Alvik expansion header
        try:
            self.shared_i2c = I2CDriver(scl=13, sda=12)
        except Exception as e:
            print(f"I2C Driver Error: {e}")
            self.shared_i2c = None

        # Dependency Injection: Pass the same driver instance to all components
        self.buzzer = Buzzer(i2c_driver=self.shared_i2c)
        self.screen = oLED(i2c_driver=self.shared_i2c)
        
        # Debounced Button instances using method handles
        self._btn_up = Button(self.alvik.get_touch_up)
        self._btn_down = Button(self.alvik.get_touch_down)
        self._btn_left = Button(self.alvik.get_touch_left)
        self._btn_right = Button(self.alvik.get_touch_right)
        self._btn_ok = Button(self.alvik.get_touch_ok)
        self._btn_cancel = Button(self.alvik.get_touch_cancel)

        print("SuperBot V44 Initialized.")

    # --- Debounced Touch Accessors ---
    def get_pressed_up(self): return self._btn_up.is_pressed()
    def get_pressed_down(self): return self._btn_down.is_pressed()
    def get_pressed_left(self): return self._btn_left.is_pressed()
    def get_pressed_right(self): return self._btn_right.is_pressed()
    def get_pressed_ok(self): return self._btn_ok.is_pressed()
    def get_pressed_cancel(self): return self._btn_cancel.is_pressed()

    def update_display(self, l1, l2="", l3=""):
        if self.screen:
            self.screen.show_lines(l1, l2, l3)

# Developed with the assistance of Google Gemini V44