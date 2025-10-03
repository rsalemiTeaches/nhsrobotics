#-------------------------------------------------------------------------------
# qwiic_buzzer.py
#
# Python library for the SparkFun Qwiic Buzzer, available here:
# https://www.sparkfun.com/products/24474
#-------------------------------------------------------------------------------
# Written by SparkFun Electronics, January 2024
#
# This python library supports the SparkFun Electroncis Qwiic ecosystem
#
# More information on Qwiic is at https://www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
#===============================================================================
# Copyright (c) 2024 SparkFun Electronics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#===============================================================================

"""
qwiic_buzzer
============
Python module for the `SparkFun Qwiic Buzzer <https://www.sparkfun.com/products/24474>`_
This is a port of the existing `Arduino Library <https://github.com/sparkfun/SparkFun_Qwiic_Buzzer_Arduino_Library>`_
This package can be used with the overall `SparkFun Qwiic Python Package <https://github.com/sparkfun/Qwiic_Py>`_
New to Qwiic? Take a look at the entire `SparkFun Qwiic ecosystem <https://www.sparkfun.com/qwiic>`_
"""
#==================================================================================

# The Qwiic_I2C_Py platform driver is designed to work on almost any Python
# platform, check it out here: https://github.com/sparkfun/Qwiic_I2C_Py
import qwiic_i2c
import time

# Define the device name and I2C addresses. These are set in the class defintion
# as class variables, making them avilable without having to create a class
# instance. This allows higher level logic to rapidly create a index of Qwiic
# devices at runtine
_DEFAULT_NAME = "Qwiic Buzzer"

# Some devices have multiple available addresses - this is a list of these
# addresses. NOTE: The first address in this list is considered the default I2C
# address for the device.
_DEFAULT_ADDRESS = 0x34
_FULL_ADDRESS_LIST = list(range(0x08, 0x77+1))  # Full address list (excluding reserved addresses)
_FULL_ADDRESS_LIST.remove(_DEFAULT_ADDRESS)   # Remove default address from list
_AVAILABLE_I2C_ADDRESS = [_DEFAULT_ADDRESS]    # Initialize with default address
_AVAILABLE_I2C_ADDRESS.extend(_FULL_ADDRESS_LIST) # Add full range of I2C addresses

# Define the class that encapsulates the device being created. All information
# associated with this device is encapsulated by this class. The device class
# should be the only value exported from this module.
class QwiicBuzzer(object):
    """
    SparkFun Qwiic Buzzer
    Initialise the Qwiic Buzzer at ``address`` with ``i2c_driver``.

    :param address:        The I2C address to use for the device.
                        If not provided, the default address is
                        used.
    :param i2c_driver:    An existing i2c driver object. If not
                        provided a driver object is created.
    
    :return:            Constructor Initialization
                        True-    Successful
                        False-    Issue loading I2C driver
    :rtype:                Bool
    """
    # Set default name and I2C address(es)
    device_name         = _DEFAULT_NAME
    available_addresses = _AVAILABLE_I2C_ADDRESS
    DEFAULT_ADDRESS = _DEFAULT_ADDRESS

    _ID = 0x5E

    # Register addresses for the Qwiic Buzzer
    _REG_ADR_ID = 0x00
    _REG_ADR_FW_MIN = 0x01
    _REG_ADR_FW_MAJ = 0x02
    _REG_ADR_FREQ_MSB = 0x03
    _REG_ADR_FREQ_LSB = 0x04
    _REG_ADR_VOL = 0x05
    _REG_ADR_DUR_MSB = 0x06
    _REG_ADR_DUR_LSB = 0x07
    _REG_ADR_ACTIVE = 0x08
    _REG_ADR_SAVE = 0x09
    _REG_ADR_I2C_ADD = 0x0A

    RESONANT_FREQUENCY = 2730

    VOLUME_MIN = 1
    VOLUME_LOW = 2
    VOLUME_MID = 3
    VOLUME_MAX = 4

    NOTE_REST = 0
    NOTE_B0  = 31
    NOTE_C1  = 33
    NOTE_CS1 = 35
    NOTE_D1  = 37
    NOTE_DS1 = 39
    NOTE_E1  = 41
    NOTE_F1  = 44
    NOTE_FS1 = 46
    NOTE_G1  = 49
    NOTE_GS1 = 52
    NOTE_A1  = 55
    NOTE_AS1 = 58
    NOTE_B1  = 62
    NOTE_C2  = 65
    NOTE_CS2 = 69
    NOTE_D2  = 73
    NOTE_DS2 = 78
    NOTE_E2  = 82
    NOTE_F2  = 87
    NOTE_FS2 = 93
    NOTE_G2  = 98
    NOTE_GS2 = 104
    NOTE_A2  = 110
    NOTE_AS2 = 117
    NOTE_B2  = 123
    NOTE_C3  = 131
    NOTE_CS3 = 139
    NOTE_D3  = 147
    NOTE_DS3 = 156
    NOTE_E3  = 165
    NOTE_F3  = 175
    NOTE_FS3 = 185
    NOTE_G3  = 196
    NOTE_GS3 = 208
    NOTE_A3  = 220
    NOTE_AS3 = 233
    NOTE_B3  = 247
    NOTE_C4  = 262
    NOTE_CS4 = 277
    NOTE_D4  = 294
    NOTE_DS4 = 311
    NOTE_E4  = 330
    NOTE_F4  = 349
    NOTE_FS4 = 370
    NOTE_G4  = 392
    NOTE_GS4 = 415
    NOTE_A4  = 440
    NOTE_AS4 = 466
    NOTE_B4  = 494
    NOTE_C5  = 523
    NOTE_CS5 = 554
    NOTE_D5  = 587
    NOTE_DS5 = 622
    NOTE_E5  = 659
    NOTE_F5  = 698
    NOTE_FS5 = 740
    NOTE_G5  = 784
    NOTE_GS5 = 831
    NOTE_A5  = 880
    NOTE_AS5 = 932
    NOTE_B5  = 988
    NOTE_C6  = 1047
    NOTE_CS6 = 1109
    NOTE_D6  = 1175
    NOTE_DS6 = 1245
    NOTE_E6  = 1319
    NOTE_F6  = 1397
    NOTE_FS6 = 1480
    NOTE_G6  = 1568
    NOTE_GS6 = 1661
    NOTE_A6  = 1760
    NOTE_AS6 = 1865
    NOTE_B6  = 1976
    NOTE_C7  = 2093
    NOTE_CS7 = 2217
    NOTE_D7  = 2349
    NOTE_DS7 = 2489
    NOTE_E7  = 2637
    NOTE_F7  = 2794
    NOTE_FS7 = 2960
    NOTE_G7  = 3136
    NOTE_GS7 = 3322
    NOTE_A7  = 3520
    NOTE_AS7 = 3729
    NOTE_B7  = 3951
    NOTE_C8  = 4186
    NOTE_CS8 = 4435
    NOTE_D8  = 4699
    NOTE_DS8 = 4978

    def __init__(self, address=None, i2c_driver=None):
        """
        Constructor

        :param address: The I2C address to use for the device
            If not provided, the default address is used
        :type address: int, optional
        :param i2c_driver: An existing i2c driver object
            If not provided, a driver object is created
        :type i2c_driver: I2CDriver, optional
        """

        # Use address if provided, otherwise pick the default
        if address in self.available_addresses:
            self.address = address
        else:
            self.address = self.available_addresses[0]

        # Load the I2C driver if one isn't provided
        if i2c_driver is None:
            self._i2c = qwiic_i2c.getI2CDriver()
            if self._i2c is None:
                print("Unable to load I2C driver for this platform.")
                return
        else:
            self._i2c = i2c_driver

    def is_connected(self):
        """
        Determines if this device is connected

        :return: `True` if connected, otherwise `False`
        :rtype: bool
        """
        # Check if connected by seeing if an ACK is received
        return self._i2c.isDeviceConnected(self.address)

    connected = property(is_connected)

    def begin(self):
        """
        Initializes this device with default parameters
        Run is_connected() and check the ID in the ID register

        :return: Returns `True` if successful, otherwise `False`
        :rtype: bool
        """
        # Confirm device is connected before doing anything
        if self.is_connected():
            id = self._i2c.readByte(self.address, self._REG_ADR_ID)
            if id == self._ID:
                return True

        return False

    def on(self):
        """
        Turns on the buzzer

        :return: Returns true if the register write has completed
        :rtype: bool
        """

        self._i2c.writeByte(self.address, self._REG_ADR_ACTIVE, 1)
    
    def off(self):
        """
        Turns off the buzzer

        :return: Returns true if the register write has completed
        :rtype: bool
        """
        
        self._i2c.writeByte(self.address, self._REG_ADR_ACTIVE, 0)

    def configure(self, frequency = RESONANT_FREQUENCY, duration = 0, volume = VOLUME_MAX):
        """
        Configures the Qwiic Buzzer without causing the buzzer to buzz.
        This allows configuration in silence (before you may want to buzz).
        It is also useful in combination with saveSettings(), and then later
        causing buzzing by using the physical TRIGGER pin.
        To start buzzing (via Qwiic) with your desired configuration, use this
        function, then call on().

        :param frequency: Frequency in Hz of buzzer tone
        :type frequency: int
        :param duration: Duration in milliseconds (0 = forever)
        :type duration: int        
        :param volume: Volume (4 settings; 0=off, 1=quiet... 4=loudest) 
        :type volume: int                   
        :return: Returns true if the register write has completed
        :rtype: bool
        """
        
        # All of the necessary configuration register addresses are in sequential order,
        # starting at "_REG_ADR_FREQ_MSB".
        # We can write all of them in a single use of "writeBlock()".

        # _REG_ADR_FREQ_MSB = 0x03,
        # _REG_ADR_FREQ_LSB = 0x04,
        # _REG_ADR_VOL = 0x05,
        # _REG_ADR_DUR_MSB = 0x06,
        # _REG_ADR_DUR_LSB = 0x07,

        # extract MSBs and LSBs from user passed in arguments
        frequencyMSB = ((frequency & 0xFF00) >> 8)
        frequencyLSB = (frequency & 0x00FF)
        durationMSB = ((duration & 0xFF00) >> 8)
        durationLSB = (duration & 0x00FF)

        data = [0,0,0,0,0]

        data[0] = frequencyMSB; # _REG_ADR_FREQ_MSB
        data[1] = frequencyLSB; # _REG_ADR_FREQ_LSB
        data[2] = volume;           # _REG_ADR_VOL
        data[3] = durationMSB;      # _REG_ADR_DUR_MSB
        data[4] = durationLSB;      # _REG_ADR_DUR_LSB

        self._i2c.writeBlock(self.address, self._REG_ADR_FREQ_MSB, data)

    def save_settings(self):
        """
        Stores settings to EEPROM

        :return: Returns true if the register write has completed
        :rtype: bool
        """
        
        self._i2c.writeByte(self.address, self._REG_ADR_SAVE, 1)

    def change_address(self, address):
        """
        Changes the I2C address of the Qwiic Buzzer    

        :param address: New address, must be in the range 0x08 to 0x77
        :type address: int
        :return: Returns `True` if successful, otherwise `False`
        :rtype: bool
        """
        # Check whether the address is valid
        if address < 0x08 or address > 0x77:
            return False

        # Write the new address to the device
        self._i2c.writeByte(self.address, self._REG_ADR_I2C_ADD, address)

        # Update the address of this object
        self.address = address

    def get_address(self):
        """
        Gets the current I2C address of the Qwiic Buzzer    

        :return: The current I2C address, 7-bit unshifted
        :rtype: int
        """
        return self.address
    
    def firware_version_major(self):
        """
        Reads the Firmware Version Major from the Qwiic Buzzer

        :return: Firmware Version Major
        :rtype: int
        """
        return self._i2c.readByte(self.address, self._REG_ADR_FW_MAJ)
    
    def firware_version_minor(self):
        """
        Reads the Firmware Version Minor from the Qwiic Buzzer

        :return: Firmware Version Minor
        :rtype: int
        """
        return self._i2c.readByte(self.address, self._REG_ADR_FW_MIN)
    
    def play_sound_effect(self, sound_effect_number = 0, volume = VOLUME_MAX):
        """
        Plays the desired sound effect at a specified volume

        :param sound_effect_number: Which sound effect you'd like to play (0-9)
        :type sound_effect_number: int
        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """

        if (sound_effect_number == 0):
            self.sound_effect_0(volume)
        elif (sound_effect_number == 1):
            self.sound_effect_1(volume)
        elif (sound_effect_number == 2):
            self.sound_effect_2(volume)
        elif (sound_effect_number == 3):
            self.sound_effect_3(volume)
        elif (sound_effect_number == 4):
            self.sound_effect_4(volume)
        elif (sound_effect_number == 5):
            self.sound_effect_5(volume)
        elif (sound_effect_number == 6):
            self.sound_effect_6(volume)
        elif (sound_effect_number == 7):
            self.sound_effect_7(volume)
        elif (sound_effect_number == 8):
            self.sound_effect_8(volume)
        elif (sound_effect_number == 9):
            self.sound_effect_9(volume)

    def sound_effect_0(self, volume):
        """
        Plays sound effect 0 (aka "Siren")
        Intended to sound like a siren, starting at a low frequency, and then
        increasing rapidly up and then back down. This sound effect does a
        single "up and down" cycle.

        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """
        for note in range (150, 4000, 150):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        for note in range (4000, 150, -150):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()

    def sound_effect_1(self, volume):
        """
        Plays sound effect 1 (aka "3 Fast Sirens")
        Intended to sound like a siren, starting at a low frequency, and then
        increasing rapidly up and then back down. This sound effect does this
        cycle of "up and down" three times rapidly.

        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """
        for i in range(3):
            for note in range (150, 4000, 150):
                self.configure(note, 0, volume)
                self.on()
                time.sleep(0.002)
            for note in range (4000, 150, -150):
                self.configure(note, 0, volume)
                self.on()
                time.sleep(0.002)
        self.off()

    def sound_effect_2(self, volume):
        """
        Plays sound effect 2 (aka "robot saying 'Yes'")
        Intended to sound like a robot saying the word "yes".
        It starts at a low frequency and quickly ramps up to a high frequency,
        then stops. This can be interpreted by most to be an affirmative
        sound to any question you may ask your buzzing robot.

        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """
        for note in range (150, 4000, 150):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.04)
        self.off()

    def sound_effect_3(self, volume):
        """
        Plays sound effect 3 (aka "robot yelling 'YES!'" - faster)
        Intended to sound like a robot saying the word "yes".
        It starts at a low frequency and quickly ramps up to a high frequency,
        then stops. This can be interpreted by most to be an affirmative
        sound to any question you may ask your buzzing robot. As this sound
        is done more quickly, it can add enthusiasm to the buzzing sound.

        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """
        for note in range (150, 4000, 150):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()

    def sound_effect_4(self, volume):
        """
        Plays sound effect 4 (aka "robot saying 'No'")
        Intended to sound like a robot saying the word "no".
        It starts at a high frequency and quickly ramps down to a low frequency,
        then stops. This can be interpreted by most to be an negative
        sound to any question you may ask your buzzing robot.

        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """
        for note in range (4000, 150, -150):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.04)
        self.off()

    def sound_effect_5(self, volume):
        """
        Plays sound effect 5 (aka "robot yelling 'NO!'" - faster)
        Intended to sound like a robot saying the word "no".
        It starts at a high frequency and quickly ramps down to a low frequency,
        then stops. This can be interpreted by most to be an negative
        sound to any question you may ask your buzzing robot. As this sound
        is done more quickly, it can add enthusiasm to the buzzing sound.

        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """
        for note in range (4000, 150, -150):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()

    def sound_effect_6(self, volume):
        """
        Plays sound effect 6 (aka "Laughing Robot")
        Intended to sound like your robot is laughing at you.

        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """
        laugh_delay = 0.4
        laugh_step = 10

        for note in range (1538, 1905, laugh_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
        time.sleep(laugh_delay)

        for note in range (1250, 1515, laugh_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
        time.sleep(laugh_delay)

        for note in range (1111, 1342, laugh_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
        time.sleep(laugh_delay)

        for note in range (1010, 1176, laugh_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()

    def sound_effect_7(self, volume):
        """
        Plays sound effect 7 (aka "Laughing Robot Faster")
        Intended to sound like your robot is laughing at you. As this sound
        is done more quickly, it can add enthusiasm to the buzzing sound.

        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """
        laugh_delay = 0.2
        laugh_step = 15

        for note in range (1538, 1905, laugh_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
        time.sleep(laugh_delay)

        for note in range (1250, 1515, laugh_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
        time.sleep(laugh_delay)

        for note in range (1111, 1342, laugh_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
        time.sleep(laugh_delay)

        for note in range (1010, 1176, laugh_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()

    def sound_effect_8(self, volume):
        """
        Plays sound effect 8 (aka "Crying Robot")
        Intended to sound like a robot is crying and sad.

        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """
        cry_delay = 0.5
        cry_step = -10

        for note in range (2000, 1429, cry_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
        time.sleep(cry_delay)

        for note in range (1667, 1250, cry_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
        time.sleep(cry_delay)

        for note in range (1429, 1053, cry_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()

    def sound_effect_9(self, volume):
        """
        Plays sound effect 9 (aka "Crying Robot Faster")
        Intended to sound like a robot is crying and sad. As this sound
        is done more quickly, it can add enthusiasm to the buzzing sound.

        :param volume: The volume of the sound effect played (1-4)
        :type volume: int
        """
        cry_delay = 0.2
        cry_step = -20

        for note in range (2000, 1429, cry_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
        time.sleep(cry_delay)

        for note in range (1667, 1250, cry_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
        time.sleep(cry_delay)

        for note in range (1429, 1053, cry_step):
            self.configure(note, 0, volume)
            self.on()
            time.sleep(0.01)
        self.off()
