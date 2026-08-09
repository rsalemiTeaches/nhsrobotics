# tests/tb/wiring.py -- the one global the fakes look at. V01
#
# The DUT builds its own ArduinoAlvik() and SuperBot() at module level, so
# the fakes cannot be handed a plant through a constructor argument. They
# reach for whatever environment is active instead. Exactly one run
# happens at a time, so a module global is the whole mechanism.

ACTIVE = None


def active():
    if ACTIVE is None:
        raise RuntimeError(
            "A fake robot was built with no environment active. The DUT was "
            "imported outside Environment.run().")
    return ACTIVE
