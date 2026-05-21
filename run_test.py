import sys
sys.path.append('nhs_lib')
sys.path.append('tests')

from tests.regression_peripherals import test_gamepad_init

class DummyBot:
    pass

bot = DummyBot()
res = test_gamepad_init(bot)
print("Result:", res)
