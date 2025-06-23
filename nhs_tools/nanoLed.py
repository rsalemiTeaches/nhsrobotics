# This program controls the small RGB LED located on the
# Arduino Nano ESP32 board itself, not the two larger Alvik LEDs.

# We import the Pin and PWM classes from the standard machine library.
from machine import Pin, PWM
import time

# Define the GPIO pins for each color of the onboard RGB LED.
# These are fixed hardware connections on the Nano ESP32 board.
NANO_LED_RED_PIN = 46
NANO_LED_GREEN_PIN = 0
NANO_LED_BLUE_PIN = 45

# --- PWM Setup ---
# To control brightness, we create a PWM (Pulse Width Modulation) object
# for each color pin. We can set a frequency for the PWM signal.
# A frequency of 1000 Hz is common for LEDs.
pwm_r = PWM(Pin(NANO_LED_RED_PIN), freq=1000)
pwm_g = PWM(Pin(NANO_LED_GREEN_PIN), freq=1000)
pwm_b = PWM(Pin(NANO_LED_BLUE_PIN), freq=1000)

# The duty cycle controls the brightness. It's a 16-bit number,
# meaning it ranges from 0 to 65535.
# IMPORTANT: The Nano ESP32's RGB LED is "active-low", which means
# a LOW signal turns it ON. So we have to invert the logic.
# 0 = max brightness
# 65535 = off

def set_nano_led_color(r, g, b):
  """
  Sets the Nano's onboard LED color.
  r, g, b are brightness values from 0 to 255.
  """
  # We convert the 0-255 scale to the inverted 0-65535 PWM scale.
  # (255 - color) scales it inversely.
  # * 257 maps the 0-255 range to the 0-65535 range (255*257 = 65535).
  pwm_r.duty_u16( (255 - r) * 257 )
  pwm_g.duty_u16( (255 - g) * 257 )
  pwm_b.duty_u16( (255 - b) * 257 )


# --- Main Program ---
print("Controlling the Nano's onboard RGB LED...")

# Set the LED to a medium-brightness purple
# Red = 128, Green = 0, Blue = 255
print("Setting color to purple.")
set_nano_led_color(128, 0, 255)
time.sleep(3)

# Set the LED to a dim yellow
# Red = 100, Green = 100, Blue = 0
print("Setting color to dim yellow.")
set_nano_led_color(25, 25, 0)
time.sleep(3)

# Turn the LED off
print("Turning LED off.")
set_nano_led_color(0, 0, 0)

print("Program finished.")

