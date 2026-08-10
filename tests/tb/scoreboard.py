# tests/tb/scoreboard.py -- the checks. V02
#
# Every check here computes its expectation from the PLANT, never from the
# DUT's own numbers. That is the whole discipline: a checker that repeats
# the DUT's arithmetic agrees with it when it is wrong.

SQUARE_TOLERANCE_DEG = 6.0


def check_run_completed(result):
    if result.error is not None:
        return 0, "DUT raised %s" % result.error
    if result.watchdog:
        return 0, "watchdog fired at %d ms -- DUT never finished" % result.sim_ms
    return 1, ""


def check_squared_up(env, tolerance_deg=SQUARE_TOLERANCE_DEG):
    """Truth check: is the robot actually perpendicular to the line?

    Read from the plant's own theta and the line's own angle. The DUT's
    reported pose is not consulted, so an over-reporting odometry cannot
    hide a real misalignment.
    """
    error = env.plant.heading_error_to_square_deg()
    if abs(error) > tolerance_deg:
        return 0, "off square by %.1f deg (tolerance %.1f)" % (error, tolerance_deg)
    return 1, ""


def check_on_the_line(env):
    """Both outer sensors over the line at the end -- square AND arrived."""
    left, _centre, right = env.plant.sensor_line_state()
    if not (left and right):
        return 0, "finished with outer sensors (left=%s right=%s)" % (left, right)
    return 1, ""


def check_no_rotate(monitor):
    """P08's standing rule: every turn watches something, so rotate() --
    which blocks and watches nothing -- must never appear."""
    if monitor.saw("rotate"):
        return 0, "called alvik.rotate(), which blocks and cannot watch a sensor"
    return 1, ""


def check_stopped_cleanly(monitor):
    if not monitor.saw("stop"):
        return 0, "never called alvik.stop(); the robot would hold the WiFi"
    if not monitor.saw("brake"):
        return 0, "never called alvik.brake(); wheels could be left running"
    return 1, ""


def check_lights_out(monitor):
    """The last thing written to either LED must be off."""
    leds = monitor.of("led")
    if not leds:
        return 2, "project never used the top LEDs"
    last = {}
    for _stamp, _kind, (name, colour) in leds:
        last[name] = colour
    still_on = [name for name, colour in last.items() if any(colour)]
    if still_on:
        return 0, "left %s lit at exit" % (", ".join(sorted(still_on)))
    return 1, ""


def check_reached_states(monitor, expected):
    seen = monitor.states_shown()
    missing = [state for state in expected if state not in seen]
    if missing:
        return 0, "never entered %s (saw %s)" % (", ".join(missing), seen)
    return 1, ""


def check_never_moved_before_sensors(env, monitor):
    """A self-check failure must not drive.

    Written against the monitor, so it catches a DUT that commands motion
    and then stops, which the final pose alone would hide.
    """
    for _stamp, kind, args in monitor.transactions:
        if kind == "drive" and any(args):
            return 0, "commanded drive%s despite dead sensors" % (args,)
        if kind == "set_wheels_speed" and any(args):
            return 0, "commanded wheels%s despite dead sensors" % (args,)
    return 1, ""


def check_stayed_in_ring(env):
    """Truth check: did the robot ever leave the sumo ring?

    Read from the plant's own position, not from anything the DUT said.
    A robot whose edge test is broken reports nothing unusual -- it just
    drives away.
    """
    ring = env.plant.ring
    if ring is None:
        return 2, "no ring in this plant"
    if env.plant.left_ring:
        return 0, ("left the ring: reached %.1f cm from centre, ring is %.1f"
                   % (env.plant.max_radius_cm, ring[0]))
    return 1, ""


def check_no_motion_before(monitor, sim_ms):
    """Nothing that moves a wheel may happen before this moment.

    Used for the start of a match: the robot is armed, the button has not
    been pressed, and a robot that creeps has jumped the start.
    """
    movers = ("drive", "set_wheels_speed", "move", "rotate")
    for stamp, kind, args in monitor.transactions:
        if kind in movers and stamp < sim_ms:
            if kind in ("drive", "set_wheels_speed") and all(
                    abs(float(a)) < 1e-9 for a in args):
                continue        # ordering a stop is not moving
            return 0, "%s at %d ms, before the start at %d ms" % (
                kind, stamp, sim_ms)
    return 1, ""
