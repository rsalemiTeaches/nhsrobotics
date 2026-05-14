# NHS Robotics (`nhs_robotics`)

Welcome to the `nhs_robotics` library! This library makes it easy to control your robot and its various components using MicroPython.

## 🤖 Optional Hardware Available
While you can use this library with just the base robot, there are several optional hardware components you can attach and control:
* **Arduino Alvik**: The base robotic platform.
* **NanoLED**: The onboard color-changing light.
* **HuskyLens**: A smart camera for detecting objects like AprilTags or faces.
* **OLED Screen**: A small screen to display text and robot status.
* **Qwiic Buzzer**: A speaker to play sounds and musical notes.

---

## 🚀 Quick Start Example

Here is a quick example of how to start your robot and make it do a few simple things!

```python
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot

# Initialize the base Alvik robot
alvik = ArduinoAlvik()
alvik.begin()

# Initialize the SuperBot with your base robot object
bot = SuperBot(alvik)

# Change the onboard LED color to green!
bot.set_nano_rgb(0, 255, 0)

# Drive forward to a black line
bot.drive_to_line(speed=15, threshold=500)

# Make the buzzer play a "YES" sound effect
if bot.buzzer:
    bot.buzzer.play_effect(bot.buzzer.EFFECT_YES)
```

---

## 📚 API Reference

Here are the commands you can use to control the different parts of your robot.

### 🚗 `SuperBot` (Main Robot Class)

The `SuperBot` class is the main brain that coordinates movement, sensors, and peripherals.

#### Setup and Basics
| Method | Description |
| :--- | :--- |
| `__init__(alvik)` | Initializes the SuperBot with your base `alvik` robot object. |
| `get_floor_status()` | Returns the status of the floor (e.g., `"SAFE"`). |

#### Nano LED Controls
| Method | Description |
| :--- | :--- |
| `set_nano_rgb(r, g, b)` | Sets the LED color using values from 0 to 255. |
| `set_nano_color(r, g, b)` | Sets the LED using simple ON/OFF values (0 or 1). |
| `set_nano_brightness(percentage)` | Changes how bright the light is (0 to 100). |
| `nano_off()` | Turns the Nano LED completely off. |

#### Student-Friendly Movement
| Method | Description |
| :--- | :--- |
| `drive_to_line(speed, threshold, blocking)` | Drives forward until it sees a black line on the floor. |
| `approach_tag(target_id, stop_distance, speed, blocking)` | Uses the camera to find an AprilTag and drive towards it until it reaches the stop distance. |
| `align_to_tag(target_id, align_dist)` | Aligns the robot straight with an AprilTag. |

#### Precise Movement & Sensors
| Method | Description |
| :--- | :--- |
| `drive_distance(distance_cm, speed_cm_s, blocking, timeout)` | Drives exactly the distance you tell it (in cm). |
| `rotate_precise(degrees)` | Turns the robot a specific number of degrees. |
| `turn_to_heading(target_angle, tolerance, timeout)` | Turns until the robot faces a specific compass heading. |
| `get_yaw()` | Returns the robot's current compass direction. |
| `get_closest_distance()` | Checks all distance sensors and returns the closest object. |

#### Display and Logging
| Method | Description |
| :--- | :--- |
| `update_display(line1, line2, line3)` | Prints up to 3 lines of text on the OLED screen. |
| `log_info(*args)` | Prints information to the console and the screen. |
| `log_error(*args)` | Prints an error message to the console and screen. |

#### Button Inputs
You can check if the touch buttons on the robot were just pressed using these methods. They return `True` or `False`.
| Method | Description |
| :--- | :--- |
| `get_pressed_up()` | Was the UP button pressed? |
| `get_pressed_down()` | Was the DOWN button pressed? |
| `get_pressed_left()` | Was the LEFT button pressed? |
| `get_pressed_right()` | Was the RIGHT button pressed? |
| `get_pressed_ok()` | Was the OK button pressed? |
| `get_pressed_cancel()` | Was the CANCEL button pressed? |

---

### 💡 `NanoLED`

Controls the onboard color LED. *Note: Usually, you just use the `bot.set_nano_rgb()` commands directly through `SuperBot` instead of making this object yourself.*

| Method | Description |
| :--- | :--- |
| `set_rgb(r, g, b)` | Sets color (0-255). |
| `set_color(r, g, b)` | Sets color on/off (0 or 1). |
| `set_brightness(percentage)` | Sets brightness (0-100). |
| `off()` | Turns the LED off. |

---

### 🎵 `Buzzer`

Controls the speaker. Access this through `bot.buzzer`!

#### Playing Sounds Example
```python
# Play the "LAUGH" sound effect
if bot.buzzer:
    bot.buzzer.play_effect(bot.buzzer.EFFECT_LAUGH)
```

| Method | Description |
| :--- | :--- |
| `set_frequency(new_frequency)` | Changes the pitch of the note. |
| `set_duration(new_duration_ms)` | Changes how long the note plays (in milliseconds). |
| `on()` | Starts playing the current frequency. |
| `off()` | Stops the sound. |
| `play_effect(effect_number)` | Plays a pre-programmed sound effect. |

**Available Sound Effects:**
* `EFFECT_SIREN`
* `EFFECT_YES`
* `EFFECT_NO`
* `EFFECT_LAUGH`
* `EFFECT_CRY`

---

### 📺 `OLED`

Controls the small screen. Access this through `bot.screen`!

| Method | Description |
| :--- | :--- |
| `show_lines(line1, line2, line3)` | Displays up to 3 short lines of text on the screen. |
| `clear()` | Erases everything on the screen. |

---

### 🔘 `Button`

Detects when a button is pressed.

| Method | Description |
| :--- | :--- |
| `is_pressed()` | Returns `True` the moment the button is touched, then resets to `False` until touched again. |
