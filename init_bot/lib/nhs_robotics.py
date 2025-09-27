###########################################################
#                NHS Robotics Helper Library              #
#                                                         #
# A collection of helper functions and classes to make    #
# programming the Alvik easier for beginner projects.     #
###########################################################

# Import necessary libraries. These are used by the helper
# functions and classes below.
import qwiic_buzzer
from qwiic_i2c.micropython_i2c import MicroPythonI2C # Use the Qwiic I2C library
from nanolib import NanoLED

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
        
        # Define dummy attributes first to prevent crashes if init fails
        self.NOTE_C4, self.NOTE_G3, self.NOTE_A3, self.NOTE_B3, self.NOTE_REST = (0,0,0,0,0)
        self.EFFECT_SIREN, self.EFFECT_YES, self.EFFECT_NO, self.EFFECT_LAUGH, self.EFFECT_CRY = (0,0,0,0,0)

        try:
            # Use the MicroPythonI2C class from the qwiic_i2c library
            # This is the correct driver that is compatible with the SparkFun library
            i2c_driver = MicroPythonI2C(scl=scl_pin, sda=sda_pin)
            
            # Create the buzzer object using the correct I2C driver
            self._buzzer = qwiic_buzzer.QwiicBuzzer(i2c_driver=i2c_driver)

            # Now, the .begin() method should work as expected.
            if self._buzzer.begin() == False:
                print("Buzzer not found. Please check your connection.")
                self._buzzer = None
                return # Stop initialization if buzzer not found
            
            print("Buzzer attached successfully.")
            # Lock the volume to LOW as requested
            self._volume = self._buzzer.VOLUME_LOW
            
            # Expose the note constants for students to use
            self.NOTE_C4 = self._buzzer.NOTE_C4
            self.NOTE_G3 = self._buzzer.NOTE_G3
            self.NOTE_A3 = self._buzzer.NOTE_A3
            self.NOTE_B3 = self._buzzer.NOTE_B3
            self.NOTE_REST = 0
            
            # Expose constants for the most useful sound effects
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
