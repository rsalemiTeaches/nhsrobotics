# forklift_bot.py
# Version: V07
# Purpose: Extends SuperBot to add specific Forklift control.
#          Logic: Servo 180 = Ground (Down), Servo 0 = Raised (Up).
#          Mapping: Level 0 (Down) -> 10 (Up).
# Updates:
#   - REFACTOR: Updated to use self.alvik instead of self.bot to match nhs_robotics.py V36.

from nhs_robotics import SuperBot
import time

class ForkLiftBot(SuperBot):
    def __init__(self, alvik_inst):
        # Initialize the parent SuperBot class
        super().__init__(alvik_inst)
        
        self.log_info("ForkLiftBot V07 Initialized.")
        
        # Configuration: Which slot is the forklift?
        # True = Servo A, False = Servo B
        self.USE_SERVO_A = True 
        
        # Track current angles
        self.angle_A = 180
        self.angle_B = 0 
        
        # Ensure fork starts on the ground
        self._set_fork_angle(180)

    def _set_fork_angle(self, angle):
        """
        Sets the servo angle using the main alvik method:
        set_servo_positions(angle_A, angle_B)
        Moves instantly to the specified angle (0-180).
        """
        # Update internal tracking for the active servo
        if self.USE_SERVO_A:
            self.angle_A = angle
        else:
            self.angle_B = angle
            
        try:
            # Call the method on the ALVIK instance (self.alvik)
            # We must pass values for BOTH servos.
            self.alvik.set_servo_positions(self.angle_A, self.angle_B)
            
        except Exception as e:
            self.log_error(f"Servo Error: {e}")

    def raise_fork(self, level=10):
        """
        Smoothly moves the fork to the specified level (0-10).
        0  = Down (180 degrees)
        10 = Up   (0 degrees)
        
        BLOCKING: This function will wait until the servo has finished moving.
        """
        # Clamp input between 0 and 10
        if level < 0: 
            level = 0
        if level > 10: 
            level = 10
        
        # Map Level (0-10) to Angle (180-0)
        target_angle = int(180 - (level * 18))
        
        start_angle = self.angle_A if self.USE_SERVO_A else self.angle_B
        
        # Determine step direction: +2 or -2
        if target_angle < start_angle:
            step = -2
        else:
            step = 2
            
        # If we are already there, just return
        if start_angle == target_angle:
            return

        # Smooth loop
        stop_val = target_angle + (-1 if step < 0 else 1)
        
        for angle in range(start_angle, stop_val, step):
            self._set_fork_angle(angle)
            time.sleep(0.02) # Short delay to control speed
            
        # Ensure we hit exactly the target at the end
        self._set_fork_angle(target_angle)
        
        # EXTRA WAIT: Just to be safe and ensure physics settles
        time.sleep(0.2)

    def lower_fork(self):
        """
        Convenience function to fully lower the fork.
        """
        self.raise_fork(0)