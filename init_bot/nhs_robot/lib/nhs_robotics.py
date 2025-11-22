# nhs_robotics.py v6 (Class-based OLED - Fully Documented)

import qwiic_buzzer
from qwiic_i2c.micropython_i2c import MicroPythonI2C as I2CDriver
from nanolib import NanoLED
from web_gamepad import WebGamepad
import ssd1306
from machine import Pin, I2C

# This print statement helps confirm the correct library is loaded.
print("Loading nhs_robotics.py v6 (Final)")


# --- oLED Display Class ---
class oLED:
    """
    A simplified interface for the 128x32 I2C OLED display.
    This class automatically handles I2C setup and provides easy-to-use
    methods for displaying text.
    """
    def __init__(self):
        # Configuration is hardcoded here so students don't need it.
        SCL_PIN = 12
        SDA_PIN = 11
        I2C_ADDRESS = 0x3c
        OLED_WIDTH = 128
        OLED_HEIGHT = 32
        
        self.display = None 
        
        try:
            # Create a native MicroPython I2C object, which the official
            # ssd1306 library is now confirmed to work with.
            i2c = I2C(1, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
            
            # Initialize the OLED display driver from the ssd1306 library
            self.display = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, I2C_ADDRESS)
            
            self.clear()
            print("OLED display initialized successfully.")

        except Exception as e:
            print(f"Error: Failed to initialize OLED display. Check connection. ({e})")

    def clear(self):
        """Clears the entire screen."""
        if self.display:
            self.display.fill(0)
            self.display.show()

    def show_lines(self, line1="", line2="", line3=""):
        """
        The easiest way to display text. Clears the screen and shows up to
        three lines of text at once.
        """
        if self.display:
            self.display.fill(0) 
            self.display.text(line1, 0, 0)
            self.display.text(line2, 0, 10)
            self.display.text(line3, 0, 20)
            self.display.show()


# --- Original code from your library ---

def get_closest_distance(d1, d2, d3, d4, d5):
    """
    Finds the minimum valid distance from the five ToF sensor zones.
    A valid reading is any positive number.
    """
    all_readings = [d1, d2, d3, d4, d5]
    valid_readings = [d for d in all_readings if d > 0]
    if not valid_readings:
        return 999
    return min(valid_readings)


class Buzzer:
    """
    A simplified interface for the SparkFun Qwiic Buzzer to make it
    easier to use for beginner robotics projects.
    """
    def __init__(self, scl_pin=12, sda_pin=11):
        """
        Initializes the connection to the buzzer by using the Alvik's
        own I2C bus.
        """
        self.frequency = 2730
        self.duration = 100
        self._buzzer = None
        
        self.NOTE_C4, self.NOTE_G3, self.NOTE_A3, self.NOTE_B3, self.NOTE_REST = (0,0,0,0,0)
        self.EFFECT_SIREN, self.EFFECT_YES, self.EFFECT_NO, self.EFFECT_LAUGH, self.EFFECT_CRY = (0,0,0,0,0)

        try:
            i2c_driver = I2CDriver(scl=scl_pin, sda=sda_pin)
            self._buzzer = qwiic_buzzer.QwiicBuzzer(i2c_driver=i2c_driver)

            if self._buzzer.begin() == False:
                print("Buzzer not found. Please check your connection.")
                self._buzzer = None
                return 
            
            print("Buzzer attached successfully.")
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

        except Exception as e:
            print(f"Error initializing buzzer: {e}")
            self._buzzer = None

    def set_frequency(self, new_frequency):
        """
        Sets the frequency (pitch) of the tone in Hertz (Hz).
        """
        self.frequency = new_frequency

    def set_duration(self, new_duration_ms):
        """
        Sets how long the buzz will last in milliseconds.
        """
        self.duration = new_duration_ms

    def on(self):
        """
        Turns the buzzer on with the currently set frequency and duration.
        """
        if self._buzzer:
            self._buzzer.configure(self.frequency, self.duration, self._volume)
            self._buzzer.on()

    def off(self):
        """
        Immediately turns the buzzer off.
        """
        if self._buzzer:
            self._buzzer.off()

    def play_effect(self, effect_number):
        """
        Plays a pre-programmed sound effect.
        Example: play_effect(my_buzzer.EFFECT_SIREN)
        """
        if self._buzzer:
            self._buzzer.play_sound_effect(effect_number, self._volume)

# This library was co-authored with Google's Gemini AI.