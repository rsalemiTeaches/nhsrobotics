import time

class RobotNavigation:
    DEGREES_PER_CM = 33.88

    MODE_IDLE = 0
    MODE_DISTANCE = 1
    MODE_APRIL_TAG = 2
    MODE_DRIVE_TO_LINE = 3

    def __init__(self, alvik, ui):
        self.alvik = alvik
        self.ui = ui
        self._current_mode = self.MODE_IDLE

        # State Variables
        self._target_encoder_value = 0
        self._drive_direction = 0
        self._drive_start_time = 0
        self._drive_timeout_ms = 0
        self._is_moving_distance = False

        self._vs_target_id = 1
        self._vs_stop_distance = 0
        self._vs_speed = 0
        self._vs_lost_count = 0
        self._vs_last_dist = 999.0

        self._lf_speed = 0
        self._lf_threshold = 500

    def rotate_precise(self, degrees):
        self.alvik.rotate(degrees)

    def drive_distance(self, distance_cm, speed_cm_s=20, blocking=True, timeout=10):
        if distance_cm == 0:
            return

        self._current_mode = self.MODE_DISTANCE
        enc_values = self.alvik.get_wheels_position()
        start_avg = (enc_values[0] + enc_values[1]) / 2.0

        delta_deg = distance_cm * self.DEGREES_PER_CM

        self._target_encoder_value = start_avg + delta_deg
        self._drive_direction = 1 if distance_cm > 0 else -1
        self._is_moving_distance = True

        self._drive_start_time = time.ticks_ms()
        self._drive_timeout_ms = timeout * 1000

        self.alvik.drive(speed_cm_s * self._drive_direction, 0)

        if blocking:
            while not self.move_complete():
                time.sleep(0.01)
            self.alvik.brake()

    def approach_tag(self, vision, target_id=1, stop_distance=8.0, speed=5, blocking=True):
        self.ui.log_info(f"Approaching ID {target_id}...")

        self._current_mode = self.MODE_APRIL_TAG
        self._vs_target_id = target_id
        self._vs_stop_distance = stop_distance
        self._vs_speed = speed
        self._vs_lost_count = 0
        self._vs_last_dist = 999.0
        
        # Attach vision temporarily for the move_complete loop
        self._active_vision = vision

        self.alvik.drive(speed, 0)

        if blocking:
            while not self.move_complete():
                time.sleep(0.05)
            self.alvik.brake()
            self._active_vision = None
            return True
        return True

    def drive_to_line(self, speed=15, threshold=500, blocking=True):
        self.ui.log_info("Driving to Line...")

        self._current_mode = self.MODE_DRIVE_TO_LINE
        self._lf_speed = speed
        self._lf_threshold = threshold

        self.alvik.drive(speed, 0)

        if blocking:
            while not self.move_complete():
                time.sleep(0.01)
            self.alvik.brake()
            return True
        return True

    def move_complete(self):
        if self._current_mode == self.MODE_DISTANCE:
            time_diff = time.ticks_diff(time.ticks_ms(), self._drive_start_time)
            if time_diff > self._drive_timeout_ms:
                self.alvik.brake()
                self._is_moving_distance = False
                self._current_mode = self.MODE_IDLE
                self.ui.log_info("Warn: Drive Timeout")
                return True

            enc_values = self.alvik.get_wheels_position()
            current_avg = (enc_values[0] + enc_values[1]) / 2.0

            finished = False
            if self._drive_direction > 0:
                if current_avg >= self._target_encoder_value:
                    finished = True
            else:
                if current_avg <= self._target_encoder_value:
                    finished = True

            if finished:
                self._is_moving_distance = False
                self._current_mode = self.MODE_IDLE
                return True

            return False

        elif self._current_mode == self.MODE_APRIL_TAG:
            vision = getattr(self, '_active_vision', None)
            if not vision or not vision.husky:
                return False
                
            try:
                vision.husky.request()
            except Exception:
                return False

            blocks = [b for b in vision.husky.blocks if b.id == self._vs_target_id]

            if not blocks:
                self._vs_lost_count += 1
                if self._vs_lost_count > 10:
                    if self._vs_last_dist < 15.0:
                        self.ui.log_info("Tag lost (Close). Blind finish.")
                        remaining = self._vs_last_dist - self._vs_stop_distance
                        if remaining > 0:
                            self.drive_distance(
                                remaining, speed_cm_s=self._vs_speed, blocking=True
                            )
                        self._current_mode = self.MODE_IDLE
                        return True
                    else:
                        self.ui.log_error("Lost Tag (Far)")
                        self.alvik.brake()
                        self._current_mode = self.MODE_IDLE
                        return True
                return False

            self._vs_lost_count = 0
            tag = blocks[0]

            if tag.width == 0:
                return False
            dist = vision.K_CONSTANT / tag.width
            self._vs_last_dist = dist

            if dist <= self._vs_stop_distance:
                self._current_mode = self.MODE_IDLE
                return True

            error = 160 - tag.xCenter
            turn_rate = error * 0.15
            if turn_rate > 30:
                turn_rate = 30
            if turn_rate < -30:
                turn_rate = -30

            self.alvik.drive(self._vs_speed, turn_rate)

            return False

        elif self._current_mode == self.MODE_DRIVE_TO_LINE:
            l, c, r = self.alvik.get_line_sensors()
            threshold = self._lf_threshold
            if l > threshold or c > threshold or r > threshold:
                self._current_mode = self.MODE_IDLE
                return True
            return False

        else:
            return True

    def turn_to_heading(self, target_angle, get_yaw_func, tolerance=2.0, timeout=5):
        self.ui.log_info(f"Turn to {target_angle:.1f}")
        start_time = time.ticks_ms()

        while True:
            if time.ticks_diff(time.ticks_ms(), start_time) > timeout * 1000:
                self.alvik.brake()
                self.ui.log_info("Turn Timeout")
                break

            current_yaw = get_yaw_func()
            error = target_angle - current_yaw

            if error > 180:
                error -= 360
            if error < -180:
                error += 360

            if abs(error) <= tolerance:
                self.alvik.brake()
                break

            rotation_speed = error * 2.0
            MAX_SPEED = 50
            MIN_SPEED = 15

            if rotation_speed > MAX_SPEED:
                rotation_speed = MAX_SPEED
            if rotation_speed < -MAX_SPEED:
                rotation_speed = -MAX_SPEED
            if 0 < rotation_speed < MIN_SPEED:
                rotation_speed = MIN_SPEED
            if -MIN_SPEED < rotation_speed < 0:
                rotation_speed = -MIN_SPEED

            self.alvik.drive(0, rotation_speed)
            time.sleep(0.01)
