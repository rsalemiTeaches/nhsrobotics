# Alvik & NHS Robotics API Reference

This reference covers the complete base `ArduinoAlvik` API, followed by the `nhs_robotics` extension library used for advanced navigation, vision, and UI.

---

## 1. Main Robot Object (`ArduinoAlvik`)

The core library provided by Arduino. This interface reflects the methods available directly on the `arduino_alvik.py` instance.

**Initialization:**
```python
from arduino_alvik import ArduinoAlvik

alvik = ArduinoAlvik()
alvik.begin()
# Your code here
alvik.stop()
```

### Lifecycle & Core
| Method                                      | Description                                                  |
| :------------------------------------------ | :----------------------------------------------------------- |
| `alvik.begin()`                             | Initializes the I2C bus and internal threads. Must be called first. |
| `alvik.stop()`                              | Shuts down the looping software threads. Use `alvik.brake()` to stop motors. |
| `alvik.set_behaviour(behaviour)`            | Sets built-in behaviours.                                    |
| `alvik.is_target_reached()`                 | Returns True if a blocking move/rotate has finished.         |
| `alvik.get_ack()` / `alvik.send_ack()`      | Low-level firmware communication.                            |

### High-Level Movement
| Method                                      | Description                                                  |
| :------------------------------------------ | :----------------------------------------------------------- |
| `alvik.move(distance, unit='cm', blocking=True)` | Moves the robot forward or backward by a specific distance.  |
| `alvik.rotate(angle, unit='deg', blocking=True)` | Rotates the robot on the spot by a specific angle.         |
| `alvik.drive(linear_vel, angular_vel)`      | Sets a continuous drive speed. Use `alvik.brake()` to stop.    |
| `alvik.get_drive_speed(linear_unit, ...)`   | Returns the current `(linear, angular)` velocities.          |
| `alvik.brake()`                               | Stops any `drive()` motion. Equivalent to `alvik.drive(0, 0)`. |

### Wheels (Direct Control)
| Method                                      | Description                                                                   |
| :------------------------------------------ | :---------------------------------------------------------------------------- |
| `alvik.set_wheels_speed(left, right, unit='rpm')` | Sets the continuous speed of each wheel individually. |
| `alvik.get_wheels_speed(unit='rpm')`            | Returns a tuple `(left, right)` of current speeds. |
| `alvik.set_wheels_position(left, right, unit='deg', blocking=True)` | Rotates wheels to specific angles. |
| `alvik.get_wheels_position(unit='deg')`         | Returns a tuple `(left, right)` of the wheels' rotation angles. |

### Servos & LEDs
| Method                               | Description                                                     |
| :----------------------------------- | :-------------------------------------------------------------- |
| `alvik.set_servo_positions(pos_A, pos_B)` | Sets the angle (0-180) for servo A and servo B simultaneously.    |
| `alvik.get_servo_positions()`             | Returns a tuple `(pos_A, pos_B)`.                               |
| `alvik.set_builtin_led(value)`            | Turns the small blue STM32 LED on/off.                          |
| `alvik.set_illuminator(value)`            | Turns the front white illuminator LED on/off.                   |
| `alvik.left_led.set_color(r, g, b)`       | Sets the Left RGB LED.                                          |
| `alvik.right_led.set_color(r, g, b)`      | Sets the Right RGB LED.                                         |

### Sensors
| Method                         | Description                                                                    | Returns                                                 |
| :----------------------------- | :----------------------------------------------------------------------------- | :------------------------------------------------------ |
| `alvik.get_distance(unit='cm')`    | Distances from the 5 front-facing Time-of-Flight sensors.              | tuple: `(l, cl, c, cr, r)` |
| `alvik.get_line_sensors()`         | Raw values from the 3 bottom-facing line-following sensors.        | tuple: `(left, center, right)`                          |
| `alvik.get_color(format='rgb')`    | Processed color values from the bottom sensor.                                 | tuple: `(r, g, b)`                                      |
| `alvik.get_color_raw()`            | Raw color values from the bottom sensor.                               | tuple: `(r, g, b)`                                      |
| `alvik.get_color_label()`          | Detected color name (e.g. "RED").                                      | str                                                     |
| `alvik.color_calibration()`        | Calibrates the color sensor against a background.                      | None                                                    |
| `alvik.get_orientation()`          | Robot's orientation from IMU.                                  | tuple: `(roll, pitch, yaw)`                             |
| `alvik.get_accelerations()`        | Linear accelerations from IMU.                                  | tuple: `(ax, ay, az)`                             |
| `alvik.get_gyros()`                | Gyroscope readings from IMU.                                  | tuple: `(gx, gy, gz)`                             |
| `alvik.get_imu()`                  | Combined acceleration and gyro readings.                                  | tuple (6 elements)                            |
| `alvik.get_pose()`                 | Estimated odometry position.                                  | tuple: `(x, y, theta)`                             |
| `alvik.reset_pose(x, y, theta)`    | Resets the internal odometry tracking.                                  | None                             |

### Physical State & Power
| Method                         | Description                                                                    | Returns                                                 |
| :----------------------------- | :----------------------------------------------------------------------------- | :------------------------------------------------------ |
| `alvik.get_shake()`                | Detects if robot is being shaken.                                      | bool                                                    |
| `alvik.get_lifted()`               | Detects if robot is lifted off the ground.                             | bool                                                    |
| `alvik.get_tilt()`                 | Current physical tilt orientation.                                     | str                                                     |
| `alvik.get_battery_charge()`       | Estimated battery percentage.                                          | int                                                     |
| `alvik.is_battery_charging()`      | True if plugged into USB power.                                        | bool                                                    |

### Touch Buttons
These return `True` if the respective capacitive touch button on the robot's top is currently being touched.
* `alvik.get_touch_ok()`
* `alvik.get_touch_cancel()`
* `alvik.get_touch_center()`
* `alvik.get_touch_up()`
* `alvik.get_touch_down()`
* `alvik.get_touch_left()`
* `alvik.get_touch_right()`
* `alvik.get_touch_any()`

---

## 2. NHS Robotics (`SuperBot`)

The `SuperBot` class is a powerful wrapper around the Alvik that provides advanced subsystems for Navigation, Vision, and UI.

**Initialization:**
```python
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot

alvik = ArduinoAlvik()
alvik.begin()

bot = SuperBot(alvik)
```

### Subsystem: Navigation (`bot.nav`)
Handles complex movements and encoders.
* `bot.nav.drive_distance(distance_cm, speed_cm_s=20, blocking=True)`: Drives exactly X centimeters using encoders.
* `bot.nav.rotate_precise(degrees)`: Rotates exactly X degrees.
* `bot.nav.turn_to_heading(target_angle, get_yaw_func, tolerance=2.0)`: Uses the IMU to turn to a specific compass heading.
* `bot.nav.approach_tag(vision, target_id=1, stop_distance=8.0, speed=5)`: Drives toward an AprilTag until a certain distance is reached.
* `bot.nav.drive_to_line(speed=15, threshold=500)`: Drives forward until the bottom sensors detect a line.

### Subsystem: Vision (`bot.vision`)
Handles the HuskyLens camera for AprilTags and object tracking.
* `bot.vision.center_on_tag(target_id=1)`: Rotates the robot to face an AprilTag directly.
* `bot.vision.align_to_tag(target_id=1, align_dist=25.0)`: Calculates the offset of a tag and maneuvers the robot so it is perfectly perpendicular to the tag.
* `bot.vision.get_camera_distance()`: Returns the estimated distance to the currently tracked block.

### Subsystem: UI & Peripherals (`bot.ui` & `bot.nano_led`)
Handles the OLED screen, buzzer, Nano ESP32 RGB LED, and logging.
* `bot.ui.log_info(*args)`: Prints a message to the console and the OLED screen.
* `bot.ui.log_error(*args)`: Logs an error with the `ERROR:` prefix to both console and OLED.
* `bot.ui.play_effect(effect_number)`: Plays a sound effect on the Qwiic Buzzer.
* `bot.nano_led.set_rgb(r, g, b)`: Sets the onboard Nano LED to an 8-bit color (0-255).
* `bot.nano_led.set_brightness(percentage)`: Adjusts the brightness of the Nano LED (0-100).
* `bot.nano_led.off()`: Turns off the Nano LED.

### Buttons (`bot.btn_up`, etc.)
Debounced button checks for the physical touch sensors.
* `bot.btn_up.is_pressed()`
* `bot.btn_down.is_pressed()`
* `bot.btn_ok.is_pressed()`
* `bot.btn_cancel.is_pressed()`
* `bot.btn_left.is_pressed()`
* `bot.btn_right.is_pressed()`

---

## 3. NHS Robotics (`RobotGamepad`)

A simplified wrapper to connect a smartphone or computer to the Alvik over Wi-Fi.

```python
from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad

alvik = ArduinoAlvik()
alvik.begin()

# Automatically creates an Access Point and waits for the user to connect
gamepad = RobotGamepad(alvik)

while True:
    gamepad.update() # Must be called in a loop!
    alvik.set_wheels_speed(gamepad.left_y * 100, gamepad.right_y * 100)
    
    if gamepad.buttons['cross']:
        print("X Button pressed!")
```

* `gamepad.update()`: Fetches the latest data over Wi-Fi.
* `gamepad.left_y`, `gamepad.right_y`, `gamepad.left_x`, `gamepad.right_x`: Joystick values (-1.0 to 1.0).
* `gamepad.buttons`: Dictionary containing button states (e.g., `['cross']`, `['circle']`, `['triangle']`, `['square']`).
