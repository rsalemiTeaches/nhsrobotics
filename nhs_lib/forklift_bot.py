# forklift_robot.py
# Purpose: Extends SuperBot to add specific Forklift control.
#          Logic: Servo 180 = Ground (Down), Servo 0 = Raised (Up).
#          Mapping: Level 0 (Down) -> 10 (Up).
#          Movement must be slow and smooth.

from nhs_robotics import SuperBot
import time

class ForkLiftBot(SuperBot):
    def __init__(self, alvik_inst):
        # Initialize the parent SuperBot class
        super().__init__(alvik_inst)
        
        self.log_info("ForkLiftBot Initialized.")
        
        # Define which servo controls the lift
        # Check your hardware: usually left_servo or right_servo
        # We assume left_servo for this example.
        if hasattr(self.bot, 'left_servo'):
            self.lift_servo = self.bot.left_servo
        else:
            # Fallback if specific attribute not found
            self.log_error("Servo setup failed: Check hardware mapping.")
            self.lift_servo = None
            
        # Track the current angle so we know where to start moving from
        self.current_angle = 180 
        
        # Ensure fork starts on the ground
        self.set_fork_angle(180)

    def set_fork_angle(self, angle):
        """
        Safely sets the servo angle and updates internal state.
        """
        # Update internal tracking
        self.current_angle = angle
        
        if self.lift_servo:
            try:
                # Try setting angle directly (common in MP libraries)
                self.lift_servo.angle = angle
            except:
                try:
                    # Fallback method
                    self.lift_servo.set_angle(angle)
                except Exception as e:
                    self.log_error(f"Servo Error: {e}")

    def raise_fork(self, level=10):
        """
        Smoothly moves the fork to the specified level (0-10).
        0  = Down (180 degrees)
        10 = Up   (0 degrees)
        """
        # Clamp input between 0 and 10
        if level < 0: level = 0
        if level > 10: level = 10
        
        self.log_info(f"Moving Fork to Level {level}...")
        
        # Map Level (0-10) to Angle (180-0)
        # Level 0 -> 180
        # Level 10 -> 0
        target_angle = int(180 - (level * 18))
        
        start_angle = self.current_angle
        
        # Determine step direction: +2 or -2
        if target_angle < start_angle:
            step = -2
        else:
            step = 2
            
        # If we are already there, just return
        if start_angle == target_angle:
            return

        # Smooth loop
        # We adjust the range 'stop' parameter to ensure we reach the target
        stop_val = target_angle + (-1 if step < 0 else 1)
        
        for angle in range(start_angle, stop_val, step):
            self.set_fork_angle(angle)
            time.sleep(0.02) # Short delay to control speed
            
        # Ensure we hit exactly the target at the end
        self.set_fork_angle(target_angle)
        self.log_info(f"Fork at Level {level} ({target_angle}deg).")

    def lower_fork(self):
        """
        Convenience function to fully lower the fork.
        """
        self.raise_fork(0)
        