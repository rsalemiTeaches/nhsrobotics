# Alvik Python API Reference (Extracted from Source)

This reference is generated directly from the `arduino_alvik.py` source code to ensure accuracy.

---

## 1. Main Robot Object (`ArduinoAlvik`)

This is the main object you will use to interact with the robot.

**Initialization:**
First, create an instance of the Alvik robot.

```python
from alvik import ArduinoAlvik
import time

# Create a single instance of the Alvik robot
bot = ArduinoAlvik()

# Begin communication and setup
bot.begin()

# --- Your code goes here ---

# Stop the robot at the end
bot.stop()
```

### High-Level Movement

These methods perform complex movements that are handled by the robot's firmware.

| Method                                      | Description                                                  |
| :------------------------------------------ | :----------------------------------------------------------- |
| `bot.move(distance, unit='cm', blocking=True)` | Moves the robot forward or backward by a specific distance.  |
| `bot.rotate(angle, unit='deg', blocking=True)` | Rotates the robot on the spot by a specific angle.         |
| `bot.drive(linear_vel, angular_vel, ...)`   | Sets a continuous drive speed. Use `bot.brake()` to stop.    |
| `bot.brake()`                               | Stops any `drive()` motion. Equivalent to `bot.drive(0, 0)`. |

### Wheels (Direct Control)

| Method                                      | Description                                                                   |
| :------------------------------------------ | :---------------------------------------------------------------------------- |
| `bot.set_wheels_speed(left, right, unit='rpm')` | Sets the continuous speed of each wheel individually. Use '%' for percentage. |
| `bot.get_wheels_speed(unit='rpm')`            | Returns a tuple `(left_speed, right_speed)`.                                  |
| `bot.set_wheels_position(left, right, ...)` | Rotates each wheel to a specific angle. `blocking=True` waits for completion.   |
| `bot.get_wheels_position(unit='deg')`         | Returns a tuple `(left_angle, right_angle)` of the wheels' rotation.          |

### Servos

| Method                               | Description                                                     |
| :----------------------------------- | :-------------------------------------------------------------- |
| `bot.set_servo_positions(pos_A, pos_B)` | Sets the angle (0-180) for servo A and servo B simultaneously.    |
| `bot.get_servo_positions()`            | Returns a tuple `(pos_A, pos_B)` of the last set servo positions. |
| `bot.servo_A.set_position(angle)`    | Sets the angle of only servo A.                                 |
| `bot.servo_B.set_position(angle)`    | Sets the angle of only servo B.                                 |

### LEDs & Sound

| Method                           | Description                                            |
| :------------------------------- | :----------------------------------------------------- |
| `bot.left_led.set_color(r, g, b)`  | Sets the Left RGB LED. `r`, `g`, `b` are `True` or `False`. |
| `bot.right_led.set_color(r, g, b)` | Sets the Right RGB LED. `r`, `g`, `b` are `True` or `False`. |
| `bot.set_illuminator(value)`       | Turns the front white illuminator LED on (`True`) or off (`False`). |
| `bot.i2c.writeto(addr, buf)`       | The library does not provide a high-level sound/buzzer API. |

### Sensors

| Method                         | Description                                                                    | Returns                                                 |
| :----------------------------- | :----------------------------------------------------------------------------- | :------------------------------------------------------ |
| `bot.get_distance(unit='cm')`    | Returns distances from the 5 front-facing Time-of-Flight sensors.              | tuple: `(left, center_left, center, center_right, right)` |
| `bot.get_line_sensors()`         | Returns the raw values from the 3 bottom-facing line-following sensors.        | tuple: `(left, center, right)`                          |
| `bot.get_color_label()`          | Returns the name of the color detected by the bottom color sensor.             | string: (e.g., "BLACK", "WHITE", "RED")                 |
| `bot.get_color_raw()`            | Returns the raw RGB values from the color sensor.                              | tuple: `(r, g, b)`                                      |
| `bot.get_orientation()`          | Returns the robot's orientation from the IMU.                                  | tuple: `(roll, pitch, yaw)`                             |
| `bot.get_pose(dist_unit, ang_unit)` | Returns the robot's estimated position and heading.                          | tuple: `(x, y, theta)`                                  |
| `bot.get_touch_ok()`             | Checks if the OK button is currently pressed.                                  | `True` or `False`                                       |
| `bot.get_shake()`                | Checks if the robot is being shaken.                                           | `True` or `False`                                       |
| `bot.get_lifted()`               | Checks if the robot has been lifted off the ground.                            | `True` or `False`                                       |

### Power

| Method                   | Description                                  |
| :----------------------- | :------------------------------------------- |
| `bot.get_battery_charge()` | Returns the estimated battery percentage.    |
| `bot.is_battery_charging()`| Returns `True` if the robot is plugged in and charging. |

### Events (Callbacks)

You can register functions to run automatically when an event happens.

| Method                                      | Description                                        |
| :------------------------------------------ | :------------------------------------------------- |
| `bot.on_touch_ok_pressed(callback)`           | Runs `callback` function when OK button is pressed.  |
| `bot.on_shake(callback)`                      | Runs `callback` function when the robot is shaken.   |
| `bot.on_lift(callback)`                       | Runs `callback` function when the robot is lifted.   |
| `bot.set_timer(mode, period, callback)`       | Runs `callback` periodically or once after a delay.  |

**Example: Event-Driven Program**

```python
from alvik import ArduinoAlvik
import time

bot = ArduinoAlvik()

def when_ok_is_pressed():
    """This function will run when the OK button is pressed."""
    print("OK button was pressed!")
    # Toggle illuminator LED
    current_state = bot.set_illuminator(not current_state)


# Register the function as a callback for the 'on_touch_ok_pressed' event
bot.on_touch_ok_pressed(when_ok_is_pressed)

# Must call bot.begin() to start threads after registering events
bot.begin() 

print("Program running... Press the OK button on the robot.")

# Keep the program alive to listen for events
while True:
    time.sleep(1)
```

