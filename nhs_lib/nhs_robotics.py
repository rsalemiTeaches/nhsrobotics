# nhs_robotics.py
# Version: V41
# 
# Includes:
# 1. Original helper classes (oLED, Buzzer, Button, Controller, NanoLED)
# 2. "SuperBot" Class: Wraps an existing ArduinoAlvik object
#
# NEW IN V41:
# - FIXED: Added missing get_pressed_left and get_pressed_right methods.
# - FIXED: Updated oLED to use SoftI2C for better compatibility with Nano ESP32.

import qwiic_buzzer
from machine import Pin, I2C, SoftI2C
import time
import ssd1306
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
    """Simplified control for the Qwiic Buzzer (if attached)."""
    EFFECT_SIREN = 0
    EFFECT_YES = 1
    EFFECT_NO = 2
    
    def __init__(self, address=0x34):
        try:
            self.buzzer = qwiic_buzzer.QwiicBuzzer(address)
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
    """Helper for the SSD1306 display using SoftI2C."""
    def __init__(self, width=128, height=64):
        try:
            # Using SoftI2C to avoid hardware bus conflicts
            self.i2c = SoftI2C(scl=Pin(13), sda=Pin(12))
            self.display = ssd1306.SSD1306_I2C(width, height, self.i2c)
            self.clear()
        except Exception as e:
            print(f"OLED Init Warning: {e}")
            self.display = None

    def clear(self):
        if self.display:
            self.display.fill(0)
            self.display.show()

    def show_lines(self, line1, line2="", line3=""):
        if self.display:
            self.display.fill(0)
            self.display.text(str(line1), 0, 0)
            self.display.text(str(line2), 0, 20)
            self.display.text(str(line3), 0, 40)
            self.display.show()

class SuperBot:
    """The NHS primary robot interface."""
    def __init__(self, alvik_instance):
        self.alvik = alvik_instance
        self.buzzer = Buzzer()
        self.screen = oLED()
        
        # Debounced Button instances
        self._btn_up = Button(self.alvik.get_touch_up)
        self._btn_down = Button(self.alvik.get_touch_down)
        self._btn_left = Button(self.alvik.get_touch_left)
        self._btn_right = Button(self.alvik.get_touch_right)
        self._btn_ok = Button(self.alvik.get_touch_ok)
        self._btn_cancel = Button(self.alvik.get_touch_cancel)

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

# Developed with the assistance of Google Gemini V41