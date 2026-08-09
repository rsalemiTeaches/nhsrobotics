# tests/tb/plant.py -- the reference model of the robot's world. V01
#
# The plant owns the truth: where the robot really is, where the line
# really is, what the sensors would really report. The DUT never sees any
# of it directly -- it sees only what the fake ArduinoAlvik hands back,
# which is the truth after the measured defects have been applied.
#
# The scoreboard checks against the plant's truth, never against the DUT's
# own numbers. A checker that recomputes the DUT's arithmetic is a mirror
# and passes whenever the DUT is wrong in an interesting way.
#
# GEOMETRY CAVEAT: the sensor placement below is a MODEL, not a
# measurement. Nobody has put calipers on an Alvik for these numbers. The
# alignment results are therefore correct up to this geometry -- which is
# fine, because P08's claim is that halving cancels a scale error, and
# that claim does not depend on the exact spacing. Measure and update if a
# test ever turns on the absolute numbers.

import math

# --- robot geometry, modelled ---
SENSOR_FORWARD_CM = 5.0        # line sensors ahead of the wheel axle
SENSOR_HALF_SPACING_CM = 1.5   # outer sensors either side of centre
LINE_HALF_WIDTH_CM = 1.0       # 2 cm tape

SENSOR_ON_VALUE = 800          # reads ABOVE threshold on the white field
SENSOR_OFF_VALUE = 100

# --- measured hardware defects, from REFERENCE.md ---
# Every one of these is a knob so a test can prove a project is immune to
# it, rather than a comment claiming so.
DEFAULT_DEFECTS = {
    "drive_scale": 0.926,       # drive() delivers 92.6% of what you ask
    "drive_lag_ms": 210,        # and takes this long to get going
    "theta_scale": 1.10,        # pose theta over-reports rotation 8-13%
    "brake_settle_ms": 500,     # brake() asks; the robot rolls on
    "sensor_dead_ms": 0,        # sensors return None this long after boot
    "yaw_offset_deg": 0.0,      # where the IMU happens to start
    "oled_present": True,       # a loose OLED silently shows nothing
}


class Plant:
    def __init__(self, line_point=(40.0, 0.0), line_angle_deg=90.0,
                 start=(0.0, 0.0, 0.0), wall_distance_cm=None, defects=None):
        self.defects = dict(DEFAULT_DEFECTS)
        if defects:
            self.defects.update(defects)

        # Truth. The DUT can never read these.
        self.x, self.y, self.theta = start
        self.line_point = line_point
        self.line_angle = line_angle_deg
        self.wall_distance_cm = wall_distance_cm

        # What reset_pose() last set the reported frame to.
        self._pose_origin = (self.x, self.y, self.theta)
        self._pose_offset = (0.0, 0.0, 0.0)

        # Commanded velocity, and how long it has been commanded, so the
        # startup lag can be modelled.
        self._cmd_v = 0.0
        self._cmd_w = 0.0
        self._cmd_age_ms = 0
        self._braking_ms = 0

        self.elapsed_ms = 0
        self.distance_travelled_cm = 0.0

    # ---------- commands in ----------

    def drive(self, forward_cms, turn_deg_s):
        if (forward_cms, turn_deg_s) != (self._cmd_v, self._cmd_w):
            self._cmd_age_ms = 0
        self._cmd_v = float(forward_cms)
        self._cmd_w = float(turn_deg_s)
        self._braking_ms = 0

    def set_wheels_speed(self, left_rpm, right_rpm):
        """Modelled, not measured. Enough to move the robot sensibly for
        the gamepad projects; no test scores absolute distance on it."""
        wheel_circumference_cm = math.pi * 3.3
        left_cms = left_rpm * wheel_circumference_cm / 60.0
        right_cms = right_rpm * wheel_circumference_cm / 60.0
        track_cm = 8.8
        self.drive((left_cms + right_cms) / 2.0,
                   math.degrees((right_cms - left_cms) / track_cm))

    def brake(self):
        self._braking_ms = self.defects["brake_settle_ms"]

    def move(self, distance_cm):
        """move() is accurate -- 495 mm on a 500 mm command."""
        self._advance_pose(distance_cm * 0.99, 0.0)

    def rotate(self, angle_deg):
        """Never measured on real hardware. Modelled as accurate, and no
        project that a test scores is allowed to use it anyway."""
        self._advance_pose(0.0, angle_deg)

    def reset_pose(self, x, y, theta):
        self._pose_origin = (self.x, self.y, self.theta)
        self._pose_offset = (x, y, theta)

    # ---------- time ----------

    def step(self, dt_ms):
        self.elapsed_ms += dt_ms
        self._cmd_age_ms += dt_ms

        if self._braking_ms > 0:
            # Rolling to a stop: still moving, at a decaying rate.
            settle = self.defects["brake_settle_ms"] or 1
            fraction = max(0.0, self._braking_ms / settle)
            self._braking_ms = max(0, self._braking_ms - dt_ms)
            if self._braking_ms == 0:
                self._cmd_v = self._cmd_w = 0.0
        else:
            fraction = 1.0
            if self._cmd_age_ms < self.defects["drive_lag_ms"]:
                fraction = 0.0

        scale = self.defects["drive_scale"] * fraction
        seconds = dt_ms / 1000.0
        self._advance_pose(self._cmd_v * scale * seconds,
                           self._cmd_w * scale * seconds)

    def _advance_pose(self, distance_cm, turn_deg):
        # Small enough steps that straight-line integration is fine; the
        # DUTs all sleep 10-50 ms, which is well under a degree per step.
        self.theta += turn_deg
        radians = math.radians(self.theta)
        self.x += distance_cm * math.cos(radians)
        self.y += distance_cm * math.sin(radians)
        self.distance_travelled_cm += abs(distance_cm)

    # ---------- sensors out ----------

    def get_pose(self):
        """Reported pose. theta carries the odometry over-report; x and y
        are handed back clean, because nothing in the course leans on
        their absolute accuracy and no measurement exists for them."""
        ox, oy, otheta = self._pose_origin
        rx, ry, rtheta = self._pose_offset
        return (rx + (self.x - ox),
                ry + (self.y - oy),
                rtheta + (self.theta - otheta) * self.defects["theta_scale"])

    def get_orientation(self):
        """(roll, pitch, yaw). Yaw is the IMU: true, but 0-360 and wrapping."""
        yaw = (self.theta + self.defects["yaw_offset_deg"]) % 360.0
        return (0.0, 0.0, yaw)

    def sensor_positions(self):
        radians = math.radians(self.theta)
        forward = (math.cos(radians), math.sin(radians))
        left = (-math.sin(radians), math.cos(radians))
        nose = (self.x + SENSOR_FORWARD_CM * forward[0],
                self.y + SENSOR_FORWARD_CM * forward[1])
        offsets = (SENSOR_HALF_SPACING_CM, 0.0, -SENSOR_HALF_SPACING_CM)
        return [(nose[0] + off * left[0], nose[1] + off * left[1])
                for off in offsets]

    def _distance_to_line(self, point):
        radians = math.radians(self.line_angle)
        direction = (math.cos(radians), math.sin(radians))
        dx = point[0] - self.line_point[0]
        dy = point[1] - self.line_point[1]
        return abs(dx * direction[1] - dy * direction[0])

    def get_line_sensors(self):
        if self.elapsed_ms < self.defects["sensor_dead_ms"]:
            return (None, None, None)
        return tuple(
            SENSOR_ON_VALUE if self._distance_to_line(p) <= LINE_HALF_WIDTH_CM
            else SENSOR_OFF_VALUE
            for p in self.sensor_positions())

    def get_distance(self):
        """Five ToF zones. Modelled as a wall straight ahead, or nothing."""
        if self.wall_distance_cm is None:
            return (0, 0, 0, 0, 0)      # no echo -- SuperBot turns this into 999
        remaining = max(0.0, self.wall_distance_cm - self.distance_travelled_cm)
        return tuple([remaining] * 5)

    # ---------- truth, for the scoreboard only ----------

    def heading_error_to_square_deg(self):
        """How far the robot's heading is from square AND facing the line.

        Square means the sensor pair is parallel to the line. Two headings
        satisfy that, 180 degrees apart, and only one of them has the
        robot facing the line -- the other has it driving away. Measuring
        modulo 180 would call both correct, which is a hole: a robot that
        turns too far ends up perpendicular, backwards, and scores clean.
        So the error is measured against the perpendicular that points at
        the line, in the range -180..180.
        """
        import math
        to_line = math.degrees(math.atan2(self.line_point[1] - self.y,
                                          self.line_point[0] - self.x))
        # Nearest perpendicular to the line, on the side the robot faces.
        best = None
        for candidate in (self.line_angle + 90.0, self.line_angle - 90.0):
            facing = (candidate - to_line + 180.0) % 360.0 - 180.0
            if best is None or abs(facing) < abs(best[1]):
                best = (candidate, facing)
        error = (self.theta - best[0] + 180.0) % 360.0 - 180.0
        return error

    def sensor_line_state(self):
        readings = self.get_line_sensors()
        return tuple(r is not None and r > 500 for r in readings)
