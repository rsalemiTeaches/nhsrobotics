# tests/tb/stimulus.py -- generated stimulus and coverage. V01
#
# Approach angles are generated, not hand-picked. Hand-picked angles test
# the cases somebody already thought of, which are exactly the cases the
# code already handles.

import random

from tb.plant import DEFAULT_DEFECTS


class ApproachStimulus:
    """One randomised way of arriving at a line.

    The line is fixed at a known place and angle; the ROBOT is what moves,
    so the scoreboard always knows the truth without reverse-engineering
    anything from the DUT.
    """

    def __init__(self, seed):
        rng = random.Random(seed)
        self.seed = seed

        # Approach angle away from square. Kept acute -- the project's
        # premise is an acute approach, and the far-crossing argument does
        # not hold past that.
        self.offset_deg = rng.choice([-1, 1]) * rng.uniform(8.0, 55.0)

        # Where along the line the robot aims, and how far back it starts.
        self.lateral_cm = rng.uniform(-12.0, 12.0)
        self.standoff_cm = rng.uniform(18.0, 45.0)

        self.line_angle_deg = rng.uniform(0.0, 360.0)

        # Defects, swept across their measured ranges.
        self.defects = dict(DEFAULT_DEFECTS)
        self.defects["theta_scale"] = rng.uniform(1.08, 1.13)
        self.defects["drive_scale"] = rng.uniform(0.90, 0.95)
        self.defects["sensor_dead_ms"] = rng.choice([0, 0, 50, 150])
        self.defects["yaw_offset_deg"] = rng.uniform(0.0, 360.0)

    def start_pose(self):
        """Robot position and heading that arrive at the line off-square
        by offset_deg.

        Square heading is line_angle + 90. Backing off along the reversed
        heading puts the robot standoff_cm short of the line, then the
        lateral term slides it along the line so it is not always aimed at
        the same spot.
        """
        import math
        heading = self.line_angle_deg + 90.0 + self.offset_deg
        radians = math.radians(heading)
        line_radians = math.radians(self.line_angle_deg)

        target_x = 40.0 + self.lateral_cm * math.cos(line_radians)
        target_y = 0.0 + self.lateral_cm * math.sin(line_radians)
        return (target_x - self.standoff_cm * math.cos(radians),
                target_y - self.standoff_cm * math.sin(radians),
                heading)

    def __repr__(self):
        return ("<approach seed=%d offset=%+.1f deg line=%.0f deg "
                "theta_scale=%.3f>" % (self.seed, self.offset_deg,
                                       self.line_angle_deg,
                                       self.defects["theta_scale"]))


class Coverage:
    """What the regression has actually exercised.

    Bins are the things that could plausibly be wrong and be missed:
    which sensor trips first, how far off square the approach was, whether
    the sensors were dead at boot, and every state the DUT announced.
    """

    APPROACH_BINS = ((8, 20), (20, 35), (35, 55))

    def __init__(self):
        self.first_sensor = set()
        self.approach_bins = set()
        self.approach_signs = set()
        self.dead_sensors = set()
        self.states = set()
        self.runs = 0

    def sample(self, stim, monitor):
        self.runs += 1
        self.approach_signs.add("left" if stim.offset_deg > 0 else "right")
        magnitude = abs(stim.offset_deg)
        for low, high in self.APPROACH_BINS:
            if low <= magnitude < high:
                self.approach_bins.add((low, high))
        self.dead_sensors.add(stim.defects["sensor_dead_ms"] > 0)
        self.states.update(monitor.states_shown())

    def holes(self, expected_states=()):
        missing = []
        for sign in ("left", "right"):
            if sign not in self.approach_signs:
                missing.append("approach from the %s" % sign)
        for span in self.APPROACH_BINS:
            if span not in self.approach_bins:
                missing.append("approach %d-%d deg off square" % span)
        if True not in self.dead_sensors:
            missing.append("sensors dead at boot")
        for state in expected_states:
            if state not in self.states:
                missing.append("state %s never reached" % state)
        return missing

    def report(self, expected_states=()):
        lines = ["  runs: %d" % self.runs,
                 "  approach sides: %s" % (sorted(self.approach_signs) or "none"),
                 "  approach bins:  %s" % sorted(self.approach_bins),
                 "  boot-dead sensors seen: %s" % sorted(self.dead_sensors),
                 "  states seen:    %s" % sorted(self.states)]
        holes = self.holes(expected_states)
        lines.append("  HOLES: %s" % ("none" if not holes else "; ".join(holes)))
        return "\n".join(lines)
