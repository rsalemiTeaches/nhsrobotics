import math

# closest_valid() lives in regression_host.py now -- it needs no robot,
# so it belongs in the suite that runs without one.

class MockBlock:
    def __init__(self, width, xCenter):
        self.width = width
        self.xCenter = xCenter

def test_calculate_approach_vector(bot):
    try:
        # Test with width 0
        zero_block = MockBlock(0, 160)
        vector = bot.vision.calculate_approach_vector(zero_block, 10.0)
        if vector.distance != 0 or vector.angle != 0:
            return 0, "Failed width=0 check"

        # Test with valid block, center aligned
        valid_block = MockBlock(20, 160)
        vector = bot.vision.calculate_approach_vector(valid_block, 10.0)

        # We don't verify exact math here as per requirement, just no exceptions
        return 1, ""
    except Exception as e:
        return 0, str(e)

def test_logging(bot):
    try:
        # Test 1: Standard single-string logging
        bot.ui.log_info("Test 1: Standard single string.")

        # Test 2: Multiple arguments of mixed types
        bot.ui.log_info("Test 2: Distance to tag", 2, "is", 12.4, "cm.")

        # Test 3: Multiple arguments with a custom separator
        bot.ui.log_info("Test 3: Target Coordinates", 150, 200, sep=" | ")

        # Test 4: Single-string error logging
        bot.ui.log_error("Test 4: Single string simulated error.")

        # Test 5: Multiple arguments error logging
        bot.ui.log_error("Test 5: Connection to", "HuskyLens", "timed out. Code:", 503)
        return 1, ""
    except Exception as e:
        return 0, str(e)
