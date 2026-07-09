# line_follower.py
# nhs_robotics V03 addition: PID line following for the Alvik's three line sensors.
#
# INSTALL: copy this file into the nhs_robotics folder on the robot, then use
# the updated __init__.py (also provided) so students can do:
#     from nhs_robotics import LineFollower
#
# OPTIONAL SuperBot integration (2 lines in superbot.py __init__):
#     from .line_follower import LineFollower
#     self.line = LineFollower(alvik)          # then: l, r = sb.line.follow(30)
#
# STUDENT-FACING CONTRACT (keep this stable):
#     lf = LineFollower(alvik)
#     left_rpm, right_rpm = lf.follow(base_speed)
#     alvik.set_wheels_speed(left_rpm, right_rpm)
# Call follow() every loop tick (~10-20 ms). It reads the sensors itself.

import time


class LineFollower:
    # Tuning constants. KP is the workhorse; KD damps wiggle; KI stays 0
    # unless the robot consistently rides one side of the line.
    KP = 45.0
    KI = 0.0
    KD = 8.0
    LINE_MIN_SUM = 150   # below this total reflectance, the line is "lost"

    def __init__(self, alvik):
        self.alvik = alvik
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = time.ticks_ms()
        self.line_lost = False

    def reset(self):
        """Clear PID state. Call after leaving the line on purpose."""
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = time.ticks_ms()
        self.line_lost = False

    def _position(self):
        """Weighted line position: -1.0 (far left) .. +1.0 (far right).
        Returns None when no line is under the sensors."""
        l, c, r = self.alvik.get_line_sensors()
        total = l + c + r
        if total < self.LINE_MIN_SUM:
            return None
        return (r - l) / total

    def follow(self, base_speed):
        """One PID step. Returns (left_rpm, right_rpm).
        If the line is lost, returns (base_speed, base_speed) and sets
        self.line_lost = True so caller code can react."""
        pos = self._position()
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self._last_time) / 1000.0
        self._last_time = now
        if dt <= 0:
            dt = 0.001

        if pos is None:
            self.line_lost = True
            return (base_speed, base_speed)
        self.line_lost = False

        error = pos
        self._integral += error * dt
        # Anti-windup clamp
        if self._integral > 1.0:
            self._integral = 1.0
        elif self._integral < -1.0:
            self._integral = -1.0
        derivative = (error - self._last_error) / dt
        self._last_error = error

        correction = (self.KP * error
                      + self.KI * self._integral
                      + self.KD * derivative)

        left = base_speed + correction
        right = base_speed - correction

        # Clamp so one wheel never reverses hard at low base speeds
        limit = abs(base_speed) * 2.0
        left = max(-limit, min(limit, left))
        right = max(-limit, min(limit, right))
        return (left, right)
