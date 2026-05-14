class RegressionRunner:
    def __init__(self):
        self.passes = 0
        self.fails = 0
        self.skips = 0

    def run_test(self, test_name, test_func, bot=None):
        try:
            if bot:
                status, message = test_func(bot)
            else:
                status, message = test_func()

            if status == 1:
                print(f"[PASS] {test_name}")
                self.passes += 1
            elif status == 2:
                print(f"[SKIP] {test_name} - {message}")
                self.skips += 1
            else:
                print(f"[FAIL] {test_name} - {message}")
                self.fails += 1
        except Exception as e:
            print(f"[FAIL] {test_name} - Exception: {e}")
            self.fails += 1

    def print_summary(self):
        print("\n" + "="*40)
        print(f"REGRESSION SUITE RESULTS")
        print(f"PASS: {self.passes} | FAIL: {self.fails} | SKIP: {self.skips}")
        print("="*40)
