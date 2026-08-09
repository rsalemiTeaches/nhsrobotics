# tests/tb/monitor.py -- the transaction stream. V01
#
# Everything the DUT does to the outside world, in order, with the sim
# timestamp. The scoreboard reads this; nothing writes to the DUT here.

class Monitor:
    def __init__(self, clock):
        self.clock = clock
        self.transactions = []

    def record(self, kind, *args):
        self.transactions.append((self.clock.now_ms, kind, args))

    # --- queries the checks use ---

    def of(self, kind):
        return [t for t in self.transactions if t[1] == kind]

    def count(self, kind):
        return len(self.of(kind))

    def saw(self, kind):
        return self.count(kind) > 0

    def display_lines(self):
        """Every distinct thing written to the OLED, in order."""
        return [args for _, kind, args in self.transactions if kind == "display"]

    def states_shown(self):
        """The state names a project put on the screen, deduplicated in
        order. Projects that display 'State: ' + name make their internal
        machine observable, which is how the state coverage is collected
        without reaching inside the DUT."""
        seen = []
        for args in self.display_lines():
            for field in args:
                text = field.strip()
                if text and text.isupper() and (not seen or seen[-1] != text):
                    seen.append(text)
        return seen

    def dump(self, limit=40):
        for stamp, kind, args in self.transactions[:limit]:
            print("  %8d ms  %-18s %s" % (stamp, kind, args if args else ""))
