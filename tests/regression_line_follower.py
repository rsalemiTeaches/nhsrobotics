# regression_line_follower.py

def test_line_follower_logic(bot):
    """Pure-logic test using a fake alvik. No wheels move."""
    try:
        from nhs_robotics import LineFollower
    except ImportError:
        return 2, "LineFollower not installed"

    class FakeAlvik:
        def __init__(self):
            self.reading = (100, 400, 100)
        def get_line_sensors(self):
            return self.reading

    fake = FakeAlvik()
    lf = LineFollower(fake)

    # Centered line -> speeds nearly equal
    l, r = lf.follow(30)
    if abs(l - r) > 5:
        return 0, f"Centered line unbalanced: {l:.1f}/{r:.1f}"

    # Line to the RIGHT -> left wheel faster (turn right)
    fake.reading = (50, 200, 500)
    lf.reset()
    l, r = lf.follow(30)
    if not l > r:
        return 0, f"Right-line correction wrong: {l:.1f}/{r:.1f}"

    # Line to the LEFT -> right wheel faster
    fake.reading = (500, 200, 50)
    lf.reset()
    l, r = lf.follow(30)
    if not r > l:
        return 0, f"Left-line correction wrong: {l:.1f}/{r:.1f}"

    # Line lost -> flag set, speeds equal
    fake.reading = (10, 10, 10)
    lf.reset()
    l, r = lf.follow(30)
    if not lf.line_lost or l != r:
        return 0, "Line-lost handling wrong"
    return 1, ""

def test_line_follower_sensors(bot):
    """Hardware sanity: real sensors feed the follower without crashing."""
    try:
        from nhs_robotics import LineFollower
    except ImportError:
        return 2, "LineFollower not installed"
    try:
        lf = LineFollower(bot.alvik)
        l, r = lf.follow(0)   # base speed 0: computes, nothing would move
        if not (isinstance(l, float) and isinstance(r, float)):
            return 0, "Non-numeric output"
        return 1, f"OK (lost={lf.line_lost})"
    except Exception as e:
        return 0, str(e)
