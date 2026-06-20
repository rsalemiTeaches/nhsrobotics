import time
import math
from qwiic_huskylens import QwiicHuskylens

class ApproachVector:
    def __init__(self, angle, distance):
        self.angle = angle
        self.distance = distance

class RobotVision:
    K_CONSTANT = 1624.0

    def __init__(self, qwiic_driver, ui, nav):
        self.husky = None
        self.ui = ui
        self.nav = nav
        
        if qwiic_driver:
            self.ui.log_info("Init HuskyLens...")
            attempts = 0
            success = False
            while attempts < 3 and not success:
                try:
                    self.husky = QwiicHuskylens(i2c_driver=qwiic_driver)
                    if self.husky.begin():
                        success = True
                        self.ui.log_info("HuskyLens OK")
                    else:
                        print(f"HuskyLens Search {attempts + 1}")
                except Exception as e:
                    print(f"Husky Search Error {attempts + 1} Error: {e}")

                if not success:
                    attempts += 1
                    time.sleep(0.5)

            if not success:
                self.husky = None
                self.ui.log_error("No HuskyLens")

    def get_camera_distance(self):
        if not self.husky:
            return None
        try:
            self.husky.request()
            if len(self.husky.blocks) > 0:
                width = self.husky.blocks[0].width
                if width > 0:
                    return self.K_CONSTANT / width
        except Exception as e:
            self.ui.log_error(f"HuskyLens distance error: {e}")
        return None

    def center_on_tag(self, target_id=1, tolerance=5):
        if not self.husky:
            return False

        self.husky.request()
        blocks = [b for b in self.husky.blocks if b.id == target_id]

        if not blocks:
            return False

        target = blocks[0]
        error_pixels = 160 - target.xCenter

        if abs(error_pixels) <= tolerance:
            return True

        pixels_per_degree = 320.0 / 60.0
        angle_to_turn = error_pixels / pixels_per_degree

        self.ui.log_info(f"Center: {error_pixels}px -> {angle_to_turn:.1f}deg")
        self.nav.rotate_precise(angle_to_turn)
        return True

    def calculate_approach_vector(self, tag_block, target_dist_cm):
        if tag_block.width == 0:
            return ApproachVector(0, 0)
        d_sight = self.K_CONSTANT / tag_block.width

        x_val = tag_block.xCenter
        pixel_offset = 160 - x_val
        pixels_per_degree = 320.0 / 60.0
        theta_deg = pixel_offset / pixels_per_degree
        theta_rad = math.radians(theta_deg)

        x_tag = d_sight * math.sin(theta_rad)
        y_tag = d_sight * math.cos(theta_rad)

        y_approach = y_tag - target_dist_cm
        x_approach = x_tag

        final_dist = math.sqrt(x_approach**2 + y_approach**2)
        final_angle_rad = math.atan2(x_approach, y_approach)
        final_angle_deg = math.degrees(final_angle_rad)

        return ApproachVector(final_angle_deg, final_dist)

    def align_to_tag(self, target_id=1, align_dist=25.0):
        self.ui.log_info("Aligning...")
        tag = None
        for _ in range(5):
            try:
                self.husky.request()
                blocks = [b for b in self.husky.blocks if b.id == target_id]
                if blocks:
                    tag = blocks[0]
                    break
            except Exception as e:
                self.ui.log_error(f"Husky request error: {e}")
            time.sleep(0.1)

        if not tag:
            self.ui.log_error("Align Fail: No Tag")
            return False

        vector = self.calculate_approach_vector(tag, align_dist)

        self.nav.rotate_precise(vector.angle)
        self.nav.drive_distance(vector.distance)
        self.nav.rotate_precise(-vector.angle)

        return self.center_on_tag(target_id=target_id)
