###########################################################
#                NHS Robotics Helper Library              #
#                                                         #
# A collection of helper functions and classes to make    #
# programming the Alvik easier for beginner projects.     #
###########################################################

# Import necessary libraries. These are used by the helper
# functions and classes below.
import qwiic_buzzer
from qwiic_i2c.micropython_i2c import MicroPythonI2C # Correct I2C library

def get_closest_distance(d1, d2, d3, d4, d5):
    """
    Finds the minimum valid distance from the five ToF sensor zones.
    A valid reading is any positive number.
    """
    # Create a list of all the sensor readings.
    all_readings = [d1, d2, d3, d4, d5]
    
    # Use a list comprehension to create a new list containing only
    # valid readings (greater than 0).
    valid_readings = [d for d in all_readings if d > 0]
    
    # If the new list is empty (no valid readings), return a large number
    # to signify that nothing is seen.
    if not valid_readings:
        return 999
        
    # If there are valid readings, return the smallest (closest) one.
    return min(valid_readings)


class Buzzer:
    """
    A simplified interface for the SparkFun Qwiic Buzzer to make it
    easier to use for beginner robotics projects.
    """
    def __init__(self, scl_pin=12, sda_pin=11):
        """
        Initializes the connection to the buzzer on the specified I2C pins.
        For Alvik, the Qwiic connector uses pins SCL=12 and SDA=11.
        """
        self.frequency = 2730  # Default frequency (resonant)
        self.duration = 100    # Default duration in ms
        self._buzzer = None    # Initialize the internal buzzer object to None

        try:
            # CORRECTED: Use the MicroPythonI2C class from the qwiic_i2c library
            i2c_driver = MicroPythonI2C(scl=scl_pin, sda=sda_pin)
            # Create the underlying QwiicBuzzer object
            self._buzzer = qwiic_buzzer.QwiicBuzzer(i2c_driver=i2c_driver)

            # Check if the buzzer is connected and initialize it
            if self._buzzer.begin() == False:
                print("Buzzer not found. Please check your connection.")
                self._buzzer = None
            else:
                print("Buzzer attached successfully.")
                # Lock the volume to LOW as requested
                self._volume = self._buzzer.VOLUME_LOW
                
                # Expose the note constants for students to use, but only
                # after we know the self._buzzer object has been created.
                self.NOTE_C4 = self._buzzer.NOTE_C4
                self.NOTE_G3 = self._buzzer.NOTE_G3
                self.NOTE_A3 = self._buzzer.NOTE_A3
                self.NOTE_B3 = self._buzzer.NOTE_B3
                self.NOTE_REST = 0 # A rest is just a frequency of 0

        except Exception as e:
            print(f"Error initializing buzzer: {e}")
            self._buzzer = None

    def set_frequency(self, new_frequency):
        """
        Sets the frequency (pitch) of the tone in Hertz (Hz).
        Example: set_frequency(440) for note A4.
        """
        self.frequency = new_frequency

    def set_duration(self, new_duration_ms):
        """
        Sets how long the buzz will last in milliseconds.
        Use 0 for a continuous buzz that must be stopped with off().
        """
        self.duration = new_duration_ms

    def on(self):
        """
        Turns the buzzer on with the currently set frequency and duration.
        If duration is set to a value > 0, it will turn off automatically.
        """
        if self._buzzer:
            self._buzzer.configure(self.frequency, self.duration, self._volume)
            self._buzzer.on()

    def off(self):
        """
        Immediately turns the buzzer off. This is only needed if you start
        a buzz with a duration of 0.
        """
        if self._buzzer:
            self._buzzer.off()
