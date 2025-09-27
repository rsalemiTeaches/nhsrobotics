from machine import Pin, PWM

class NanoLED:
    """
    A singleton helper class to control the Alvik's onboard Nano ESP32 RGB LED.
    This ensures that there is only one controlling object for the physical LED,
    preventing hardware conflicts.
    """
    _instance = None

    # Define the GPIO pins for each color channel
    _RED_PIN = 46
    _GREEN_PIN = 0
    _BLUE_PIN = 45

    def __new__(cls):
        """Implements the singleton pattern."""
        if cls._instance is None:
            cls._instance = super(NanoLED, cls).__new__(cls)
            # Add a flag to ensure one-time initialization.
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initializes the RGB LED's state and hardware controllers.
        The _initialized flag prevents this from running more than once.
        """
        if self._initialized:
            return
            
        # Create and store the Pin objects once to be reused.
        self._red_pin_obj = Pin(self._RED_PIN, Pin.OUT)
        self._green_pin_obj = Pin(self._GREEN_PIN, Pin.OUT)
        self._blue_pin_obj = Pin(self._BLUE_PIN, Pin.OUT)
        
        # The PWM attributes will hold either PWM objects or None.
        self._red_pwm = None
        self._green_pwm = None
        self._blue_pwm = None

        # Store the current color and brightness state
        self._color = (0, 0, 0)
        self._brightness = 1.0  # Brightness as a float from 0.0 to 1.0
        
        # Start with the LED fully off and mark as initialized.
        self.off()
        self._initialized = True

    def set_color(self, r, g, b):
        """
        Sets the color of the LED.
        
        Args:
            r (int): The red value, from 0 to 255.
            g (int): The green value, from 0 to 255.
            b (int): The blue value, from 0 to 255.
        """
        self._color = (r, g, b)
        self._update_led()

    def set_brightness(self, percentage):
        """
        Sets the overall brightness of the LED.
        
        Args:
            percentage (int): The brightness level, from 0 to 100.
        """
        # Clamp the value between 0 and 100
        if percentage < 0: percentage = 0
        if percentage > 100: percentage = 100
            
        self._brightness = percentage / 100.0
        self._update_led()
        
    def _init_pwm(self):
        """Internal method to initialize PWM objects if they are not already active."""
        if self._red_pwm is None:
            self._red_pwm = PWM(self._red_pin_obj, freq=1000)
            self._green_pwm = PWM(self._green_pin_obj, freq=1000)
            self._blue_pwm = PWM(self._blue_pin_obj, freq=1000)

    def _update_led(self):
        """
        Internal function to apply the current color and brightness to the LED.
        """
        self._init_pwm() # Ensure PWM controllers are active

        r, g, b = self._color
        
        # Apply the brightness factor
        bright_r = r * self._brightness
        bright_g = g * self._brightness
        bright_b = b * self._brightness
        
        # For a common anode LED, duty 1023 is OFF, and 0 is FULL BRIGHTNESS.
        duty_r = int(max(0, 1023 - (bright_r * 4)))
        duty_g = int(max(0, 1023 - (bright_g * 4)))
        duty_b = int(max(0, 1023 - (bright_b * 4)))

        # Set the duty cycle for each pin
        self._red_pwm.duty(duty_r)
        self._green_pwm.duty(duty_g)
        self._blue_pwm.duty(duty_b)

    def off(self):
        """
        Turns the LED completely off by stopping the PWM signals and driving the
        pins HIGH.
        """
        if self._red_pwm is not None:
            self._red_pwm.deinit()
            self._green_pwm.deinit()
            self._blue_pwm.deinit()
            
            self._red_pwm = None
            self._green_pwm = None
            self._blue_pwm = None
        
        # Force the pins HIGH (off state for common-anode)
        Pin(self._RED_PIN, Pin.OUT).value(1)
        Pin(self._GREEN_PIN, Pin.OUT).value(1)
        Pin(self._BLUE_PIN, Pin.OUT).value(1)
        
    def __del__(self):
        """
        Destructor to ensure the LED is turned off.
        """
        self.off()

