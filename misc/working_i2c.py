commit 7fc99e7363895934fcdc15d0b878b519c6e5f3cb
Author: Ray Salemi <ray@raysalemi.com>
Date:   Wed Dec 31 16:21:01 2025 -0500

    replaced bot with alivk in SuperBot

diff --git a/dev/capstone.py b/dev/capstone.py
index b8ee024..45be18c 100644
--- a/dev/capstone.py
+++ b/dev/capstone.py
@@ -1,8 +1,8 @@
 # capstone.py
-# Version: V27
-# Purpose: Capstone solution consistent with nhs_robotics.py V35.
+# Version: V29
+# Purpose: Capstone solution consistent with nhs_robotics.py V36.
 # Logic: Find Tag -> Align -> Approach -> Lift -> Spin -> Return -> Drop.
-# Notes: Renamed robot -> forklift per instructions.
+# Notes: Updated to use forklift.alvik instead of forklift.bot.
 
 from arduino_alvik import ArduinoAlvik
 from nhs_robotics import Button
@@ -37,20 +37,20 @@ alvik.begin()
 forklift = ForkLiftBot(alvik)
 forklift.enable_info_logging()
 
-forklift.log_info("Initializing Capstone V27...")
+forklift.log_info("Initializing Capstone V29...")
 
 # Hardware Check
 if forklift.husky is None:
     forklift.log_error("CRITICAL: HuskyLens not found.")
     while True:
-        forklift.bot.left_led.set_color(1, 0, 0)
+        forklift.alvik.left_led.set_color(1, 0, 0)
         time.sleep(0.5)
-        forklift.bot.left_led.set_color(0, 0, 0)
+        forklift.alvik.left_led.set_color(0, 0, 0)
         time.sleep(0.5)
 
 # Input Buttons
-btn_start = Button(forklift.bot.get_touch_center)
-btn_cancel = Button(forklift.bot.get_touch_cancel)
+btn_start = Button(forklift.alvik.get_touch_center)
+btn_cancel = Button(forklift.alvik.get_touch_cancel)
 
 # Global Variables
 current_state = STATE_IDLE
@@ -63,15 +63,15 @@ try:
         # STATE: IDLE
         # ------------------------------------------------------------------
         if current_state == STATE_IDLE:
-            forklift.update_display("Capstone V27", "Center: START", "Cancel: EXIT")
+            forklift.update_display("Capstone V29", "Center: START", "Cancel: EXIT")
             
             # Blink Blue
             if (time.ticks_ms() // 500) % 2 == 0:
-                forklift.bot.left_led.set_color(0, 0, 1) 
-                forklift.bot.right_led.set_color(0, 0, 1)
+                forklift.alvik.left_led.set_color(0, 0, 1) 
+                forklift.alvik.right_led.set_color(0, 0, 1)
             else:
-                forklift.bot.left_led.set_color(0, 0, 0) 
-                forklift.bot.right_led.set_color(0, 0, 0)
+                forklift.alvik.left_led.set_color(0, 0, 0) 
+                forklift.alvik.right_led.set_color(0, 0, 0)
             
             if btn_cancel.get_touch():
                 forklift.log_info("Exit requested.")
@@ -79,8 +79,8 @@ try:
                 
             if btn_start.get_touch():
                 forklift.log_info("Mission Start...")
-                forklift.bot.left_led.set_color(0, 0, 0)
-                forklift.bot.right_led.set_color(0, 0, 0)
+                forklift.alvik.left_led.set_color(0, 0, 0)
+                forklift.alvik.right_led.set_color(0, 0, 0)
                 forklift.lower_fork()
                 current_state = STATE_ALIGN
 
@@ -132,7 +132,7 @@ try:
         # ------------------------------------------------------------------
         elif current_state == STATE_RETURN_SPIN:
             forklift.log_info("Spinning 180...")
-            forklift.bot.rotate(180)
+            forklift.alvik.rotate(180)
             current_state = STATE_RETURN_DRIVE
 
         # ------------------------------------------------------------------
@@ -159,8 +159,8 @@ try:
         # ------------------------------------------------------------------
         elif current_state == STATE_SUCCESS:
             forklift.log_info("MISSION COMPLETE")
-            forklift.bot.left_led.set_color(0, 1, 0)
-            forklift.bot.right_led.set_color(0, 1, 0)
+            forklift.alvik.left_led.set_color(0, 1, 0)
+            forklift.alvik.right_led.set_color(0, 1, 0)
             time.sleep(3)
             current_state = STATE_IDLE
 
@@ -169,8 +169,8 @@ try:
         # ------------------------------------------------------------------
         elif current_state == STATE_FAIL:
             forklift.log_error("MISSION FAILED")
-            forklift.bot.left_led.set_color(1, 0, 0)
-            forklift.bot.right_led.set_color(1, 0, 0)
+            forklift.alvik.left_led.set_color(1, 0, 0)
+            forklift.alvik.right_led.set_color(1, 0, 0)
             time.sleep(3)
             current_state = STATE_IDLE
         
@@ -181,9 +181,9 @@ except KeyboardInterrupt:
 except Exception as e:
     forklift.log_error(f"Critical Error: {e}")
 finally:
-    forklift.bot.stop()
-    forklift.bot.left_led.set_color(0, 0, 0)
-    forklift.bot.right_led.set_color(0, 0, 0)
+    forklift.alvik.stop()
+    forklift.alvik.left_led.set_color(0, 0, 0)
+    forklift.alvik.right_led.set_color(0, 0, 0)
     forklift.log_info("Program terminated.")
 
 # Developed with the assistance of Google Gemini
\ No newline at end of file
diff --git a/dev/capstone_student.py b/dev/capstone_student.py
index 03227c2..824c9c9 100644
--- a/dev/capstone_student.py
+++ b/dev/capstone_student.py
@@ -56,14 +56,14 @@ if forklift.husky is None:
     forklift.log_error("Camera Error!")
     while True:
         # Flash Red light forever
-        forklift.bot.left_led.set_color(1, 0, 0)
+        forklift.alvik.left_led.set_color(1, 0, 0)
         time.sleep(0.5)
-        forklift.bot.left_led.set_color(0, 0, 0)
+        forklift.alvik.left_led.set_color(0, 0, 0)
         time.sleep(0.5)
 
 # Buttons
-start_button = Button(forklift.bot.get_touch_center)
-cancel_button = Button(forklift.bot.get_touch_cancel)
+start_button = Button(forklift.alvik.get_touch_center)
+cancel_button = Button(forklift.alvik.get_touch_cancel)
 
 # Start in IDLE state
 current_state = STATE_IDLE
@@ -84,11 +84,11 @@ try:
             forklift.update_display("Ready...", "Press Center")
             
             # Blink Blue lights like in previous projects
-            forklift.bot.left_led.set_color(0, 0, 1)
-            forklift.bot.right_led.set_color(0, 0, 1)
+            forklift.alvik.left_led.set_color(0, 0, 1)
+            forklift.alvik.right_led.set_color(0, 0, 1)
             time.sleep(0.2)
-            forklift.bot.left_led.set_color(0, 0, 0)
-            forklift.bot.right_led.set_color(0, 0, 0)
+            forklift.alvik.left_led.set_color(0, 0, 0)
+            forklift.alvik.right_led.set_color(0, 0, 0)
             time.sleep(0.2)
             
             if start_button.get_touch():
@@ -149,7 +149,7 @@ try:
         # ----------------------------------------------------------------
         elif current_state == STATE_RETURN_SPIN:
             forklift.log_info("Turning around...")
-            forklift.bot.rotate(180) # Simple 180 turn
+            forklift.alvik.rotate(180) # Simple 180 turn
             time.sleep(0.5)
             current_state = STATE_RETURN_DRIVE
 
@@ -160,16 +160,16 @@ try:
             forklift.log_info("Driving home...")
             
             # Start driving forward
-            forklift.bot.drive(RETURN_SPEED, 0)
+            forklift.alvik.drive(RETURN_SPEED, 0)
             
             # Loop until we see the line
             while True:
                 # Read sensors
-                l, c, r = forklift.bot.get_line_sensors()
+                l, c, r = forklift.alvik.get_line_sensors()
                 
                 # Check if ANY sensor sees the black line (> 500)
                 if l > BLACK_LINE_THRESHOLD or c > BLACK_LINE_THRESHOLD or r > BLACK_LINE_THRESHOLD:
-                    forklift.bot.brake() # STOP!
+                    forklift.alvik.brake() # STOP!
                     forklift.log_info("Home found!")
                     break # Exit the loop
                 
@@ -191,8 +191,8 @@ try:
         # ----------------------------------------------------------------
         elif current_state == STATE_DONE:
             forklift.log_info("Success!")
-            forklift.bot.left_led.set_color(0, 1, 0) # Green
-            forklift.bot.right_led.set_color(0, 1, 0)
+            forklift.alvik.left_led.set_color(0, 1, 0) # Green
+            forklift.alvik.right_led.set_color(0, 1, 0)
             time.sleep(2)
             current_state = STATE_IDLE # Go back to start
 
@@ -200,8 +200,8 @@ try:
         # STATE 99: ERROR (Failure)
         # ----------------------------------------------------------------
         elif current_state == STATE_ERROR:
-            forklift.bot.left_led.set_color(1, 0, 0) # Red
-            forklift.bot.right_led.set_color(1, 0, 0)
+            forklift.alvik.left_led.set_color(1, 0, 0) # Red
+            forklift.alvik.right_led.set_color(1, 0, 0)
             time.sleep(2)
             current_state = STATE_IDLE
 
@@ -211,6 +211,6 @@ except KeyboardInterrupt:
     print("Stopped by user.")
 
 finally:
-    forklift.bot.stop()
+    forklift.alvik.stop()
 
 # Developed with the assistance of Google Gemini
\ No newline at end of file
diff --git a/nhs_lib/forklift_bot.py b/nhs_lib/forklift_bot.py
index 72d5907..d041f05 100644
--- a/nhs_lib/forklift_bot.py
+++ b/nhs_lib/forklift_bot.py
@@ -1,13 +1,10 @@
 # forklift_bot.py
-# Version: V05
+# Version: V07
 # Purpose: Extends SuperBot to add specific Forklift control.
 #          Logic: Servo 180 = Ground (Down), Servo 0 = Raised (Up).
 #          Mapping: Level 0 (Down) -> 10 (Up).
 # Updates:
-#   - FIXED: Uses 'set_servo_positions(pos_A, pos_B)' from ArduinoAlvik class.
-#   - Assumes Forklift is on Servo A.
-#   - Keeps Servo B static at 0.
-#   - V05: raise_fork is now BLOCKING (it waits until movement is done).
+#   - REFACTOR: Updated to use self.alvik instead of self.bot to match nhs_robotics.py V36.
 
 from nhs_robotics import SuperBot
 import time
@@ -17,7 +14,7 @@ class ForkLiftBot(SuperBot):
         # Initialize the parent SuperBot class
         super().__init__(alvik_inst)
         
-        self.log_info("ForkLiftBot V05 Initialized.")
+        self.log_info("ForkLiftBot V07 Initialized.")
         
         # Configuration: Which slot is the forklift?
         # True = Servo A, False = Servo B
@@ -42,9 +39,9 @@ class ForkLiftBot(SuperBot):
             self.angle_B = angle
             
         try:
-            # Call the method on the ALVIK instance (self.bot), not a servo object.
+            # Call the method on the ALVIK instance (self.alvik)
             # We must pass values for BOTH servos.
-            self.bot.set_servo_positions(self.angle_A, self.angle_B)
+            self.alvik.set_servo_positions(self.angle_A, self.angle_B)
             
         except Exception as e:
             self.log_error(f"Servo Error: {e}")
diff --git a/nhs_lib/nhs_robotics.py b/nhs_lib/nhs_robotics.py
index 34a2c13..0df23d2 100644
--- a/nhs_lib/nhs_robotics.py
+++ b/nhs_lib/nhs_robotics.py
@@ -1,14 +1,13 @@
 # nhs_robotics.py
-# Version: V35
+# Version: V36
 # 
 # Includes:
 # 1. Original helper classes (oLED, Buzzer, Button, Controller, NanoLED)
 # 2. "SuperBot" Class: Wraps an existing ArduinoAlvik object to add features
 #
-# NEW IN V35:
-# - Reverted MODE_APRIL_TAG actuation to use self.bot.drive() (cm/s, deg/s) 
-#   instead of set_wheels_speed (RPM) to fix unit mismatch and speed issues.
-# - Blind finish logic remains, relying on accurate cm/s driving.
+# NEW IN V36:
+# - REFACTOR: Renamed self.bot -> self.alvik for student consistency.
+# - Students can now access sb.alvik.left_led, etc.
 
 # --- IMPORTS ---
 import qwiic_buzzer
@@ -23,7 +22,7 @@ from nanolib import NanoLED
 
 from qwiic_huskylens import QwiicHuskylens
 
-print("Loading nhs_robotics.py V35")
+print("Loading nhs_robotics.py V36")
 
 # --- HELPER FUNCTIONS (Legacy Bridge) ---
 
@@ -118,8 +117,7 @@ class oLED:
             try:
                 self.display.fill(0)
                 self.display.show()
-            except:  # noqa: E722
-                pass
+            except: pass
 
     def show_lines(self, line1="", line2="", line3=""):
         if self.display:
@@ -129,8 +127,7 @@ class oLED:
                 self.display.text(str(line2), 0, 10)
                 self.display.text(str(line3), 0, 20)
                 self.display.show()
-            except:  # noqa: E722
-                pass
+            except: pass
 
 class Buzzer:
     def __init__(self, scl_pin=12, sda_pin=11, i2c_driver=None):
@@ -144,7 +141,7 @@ class Buzzer:
             if i2c_driver is None:
                 i2c_driver = I2CDriver(scl=scl_pin, sda=sda_pin)
             self._buzzer = qwiic_buzzer.QwiicBuzzer(i2c_driver=i2c_driver)
-            if not self._buzzer.begin():
+            if self._buzzer.begin() == False:
                 self._buzzer = None
                 return 
             self._volume = self._buzzer.VOLUME_LOW
@@ -191,8 +188,8 @@ class SuperBot:
     MODE_APRIL_TAG = 2 
     MODE_DRIVE_TO_LINE = 3 
 
-    def __init__(self, robot):
-        self.bot = robot
+    def __init__(self, alvik):
+        self.alvik = alvik # REFACTOR: Was self.bot
         
         # --- CONSTANTS ---
         self.K_CONSTANT = 1624.0
@@ -214,9 +211,9 @@ class SuperBot:
         self._init_peripherals()
         
         if self.husky:
-            print("uperBot Init Complete. HuskyLens is active.")
+            print(f"SuperBot Init Complete. HuskyLens is active.")
         else:
-            print("SuperBot Init Complete. HuskyLens is NONE.")
+            print(f"SuperBot Init Complete. HuskyLens is NONE.")
 
         # --- STATE VARIABLES ---
         self._current_mode = self.MODE_IDLE
@@ -253,7 +250,7 @@ class SuperBot:
         if self.shared_i2c:
             try:
                 self.screen = oLED(i2cDriver=self.shared_i2c)
-                self.screen.show_lines("SuperBot", "Online", "V35")
+                self.screen.show_lines("SuperBot", "Online", "V36")
             except Exception:
                 pass
 
@@ -325,9 +322,9 @@ class SuperBot:
             
         vector = self.calculate_approach_vector(tag, align_dist)
         
-        self.bot.rotate(vector.angle)
+        self.alvik.rotate(vector.angle)
         self.drive_distance(vector.distance)
-        self.bot.rotate(-vector.angle)
+        self.alvik.rotate(-vector.angle)
         
         return self.center_on_tag(target_id=target_id)
 
@@ -348,13 +345,13 @@ class SuperBot:
         self._vs_last_dist = 999.0
         
         # Start moving (Straight initially)
-        self.bot.drive(speed, 0)
+        self.alvik.drive(speed, 0)
         
         if blocking:
             while not self.move_complete():
                 time.sleep(0.05)
             # Explicit braking because move_complete is now a pure query
-            self.bot.brake()
+            self.alvik.brake()
             return True
         
         return True
@@ -370,13 +367,13 @@ class SuperBot:
         self._lf_speed = speed
         self._lf_threshold = threshold
         
-        self.bot.drive(speed, 0)
+        self.alvik.drive(speed, 0)
         
         if blocking:
             while not self.move_complete():
                 time.sleep(0.01)
             # Explicit braking
-            self.bot.brake()
+            self.alvik.brake()
             return True
             
         return True
@@ -384,7 +381,7 @@ class SuperBot:
     # --- SENSOR METHODS ---
 
     def get_closest_distance(self):
-        d_tuple = self.bot.get_distance()
+        d_tuple = self.alvik.get_distance()
         return self._get_closest_distance(d_tuple[0], d_tuple[1], d_tuple[2], d_tuple[3], d_tuple[4])
         
     def get_camera_distance(self):
@@ -410,11 +407,11 @@ class SuperBot:
         time.sleep(duration_ms / 1000.0)
 
     def rotate_precise(self, degrees):
-        self.bot.rotate(degrees)
+        self.alvik.rotate(degrees)
         
     def get_yaw(self):
         try:
-            return self.bot.get_orientation()[2]
+            return self.alvik.get_orientation()[2]
         except:
             return 0.0
 
@@ -424,7 +421,7 @@ class SuperBot:
         
         while True:
             if time.ticks_diff(time.ticks_ms(), start_time) > timeout * 1000:
-                self.bot.brake()
+                self.alvik.brake()
                 self.log_info("Turn Timeout")
                 break
 
@@ -435,7 +432,7 @@ class SuperBot:
             if error < -180: error += 360
             
             if abs(error) <= tolerance:
-                self.bot.brake()
+                self.alvik.brake()
                 break
             
             rotation_speed = error * 2.0
@@ -447,7 +444,7 @@ class SuperBot:
             if rotation_speed > 0 and rotation_speed < MIN_SPEED: rotation_speed = MIN_SPEED
             if rotation_speed < 0 and rotation_speed > -MIN_SPEED: rotation_speed = -MIN_SPEED
             
-            self.bot.drive(0, rotation_speed)
+            self.alvik.drive(0, rotation_speed)
             time.sleep(0.01)
 
     def center_on_tag(self, target_id=1, tolerance=5):
@@ -533,7 +530,7 @@ class SuperBot:
             return
 
         self._current_mode = self.MODE_DISTANCE
-        enc_values = self.bot.get_wheels_position()
+        enc_values = self.alvik.get_wheels_position()
         start_avg = (enc_values[0] + enc_values[1]) / 2.0
         
         delta_deg = distance_cm * self.DEGREES_PER_CM
@@ -546,13 +543,13 @@ class SuperBot:
         self._drive_timeout_ms = timeout * 1000
         
         # Start moving
-        self.bot.drive(speed_cm_s * self._drive_direction, 0)
+        self.alvik.drive(speed_cm_s * self._drive_direction, 0)
         
         if blocking:
             while not self.move_complete():
                 time.sleep(0.01)
             # Explicit braking
-            self.bot.brake()
+            self.alvik.brake()
 
     def move_complete(self):
         """
@@ -565,13 +562,13 @@ class SuperBot:
         if self._current_mode == self.MODE_DISTANCE:
             # Timeout Check
             if time.ticks_diff(time.ticks_ms(), self._drive_start_time) > self._drive_timeout_ms:
-                self.bot.brake() # Safety brake
+                self.alvik.brake() # Safety brake
                 self._is_moving_distance = False
                 self._current_mode = self.MODE_IDLE
                 self.log_info("Warn: Drive Timeout")
                 return True
 
-            enc_values = self.bot.get_wheels_position()
+            enc_values = self.alvik.get_wheels_position()
             current_avg = (enc_values[0] + enc_values[1]) / 2.0
             
             finished = False
@@ -614,7 +611,7 @@ class SuperBot:
                         return True
                     else:
                         self.log_error("Lost Tag (Far)")
-                        self.bot.brake() # Safety brake
+                        self.alvik.brake() # Safety brake
                         self._current_mode = self.MODE_IDLE
                         return True
                 return False 
@@ -638,13 +635,13 @@ class SuperBot:
             
             # FIXED: Use drive(linear, angular) for cm/s + deg/s
             # NOT set_wheels_speed(RPM)
-            self.bot.drive(self._vs_speed, turn_rate)
+            self.alvik.drive(self._vs_speed, turn_rate)
             
             return False
 
         # --- MODE 3: DRIVE TO LINE ---
         elif self._current_mode == self.MODE_DRIVE_TO_LINE:
-            l, c, r = self.bot.get_line_sensors()
+            l, c, r = self.alvik.get_line_sensors()
             if l > self._lf_threshold or c > self._lf_threshold or r > self._lf_threshold:
                 self._current_mode = self.MODE_IDLE
                 return True
diff --git a/solutions/project18_sol_amazon_inv_bot.py b/solutions/project18_sol_amazon_inv_bot.py
index b8ee024..8c97b16 100644
--- a/solutions/project18_sol_amazon_inv_bot.py
+++ b/solutions/project18_sol_amazon_inv_bot.py
@@ -1,12 +1,12 @@
 # capstone.py
 # Version: V27
-# Purpose: Capstone solution consistent with nhs_robotics.py V35.
+# Purpose: Capstone solution consistent with nhs_roalvikics.py V35.
 # Logic: Find Tag -> Align -> Approach -> Lift -> Spin -> Return -> Drop.
-# Notes: Renamed robot -> forklift per instructions.
+# Notes: Renamed roalvik -> forklift per instructions.
 
 from arduino_alvik import ArduinoAlvik
-from nhs_robotics import Button
-from forklift_bot import ForkLiftBot
+from nhs_roalvikics import Button
+from forklift_alvik import ForkLiftalvik
 import time
 import sys
 
@@ -33,8 +33,8 @@ STATE_EXIT              = 99
 alvik = ArduinoAlvik()
 alvik.begin()
 
-# Instantiate ForkLiftBot
-forklift = ForkLiftBot(alvik)
+# Instantiate ForkLiftalvik
+forklift = ForkLiftalvik(alvik)
 forklift.enable_info_logging()
 
 forklift.log_info("Initializing Capstone V27...")
@@ -43,14 +43,14 @@ forklift.log_info("Initializing Capstone V27...")
 if forklift.husky is None:
     forklift.log_error("CRITICAL: HuskyLens not found.")
     while True:
-        forklift.bot.left_led.set_color(1, 0, 0)
+        forklift.alvik.left_led.set_color(1, 0, 0)
         time.sleep(0.5)
-        forklift.bot.left_led.set_color(0, 0, 0)
+        forklift.alvik.left_led.set_color(0, 0, 0)
         time.sleep(0.5)
 
 # Input Buttons
-btn_start = Button(forklift.bot.get_touch_center)
-btn_cancel = Button(forklift.bot.get_touch_cancel)
+btn_start = Button(forklift.alvik.get_touch_center)
+btn_cancel = Button(forklift.alvik.get_touch_cancel)
 
 # Global Variables
 current_state = STATE_IDLE
@@ -67,11 +67,11 @@ try:
             
             # Blink Blue
             if (time.ticks_ms() // 500) % 2 == 0:
-                forklift.bot.left_led.set_color(0, 0, 1) 
-                forklift.bot.right_led.set_color(0, 0, 1)
+                forklift.alvik.left_led.set_color(0, 0, 1) 
+                forklift.alvik.right_led.set_color(0, 0, 1)
             else:
-                forklift.bot.left_led.set_color(0, 0, 0) 
-                forklift.bot.right_led.set_color(0, 0, 0)
+                forklift.alvik.left_led.set_color(0, 0, 0) 
+                forklift.alvik.right_led.set_color(0, 0, 0)
             
             if btn_cancel.get_touch():
                 forklift.log_info("Exit requested.")
@@ -79,8 +79,8 @@ try:
                 
             if btn_start.get_touch():
                 forklift.log_info("Mission Start...")
-                forklift.bot.left_led.set_color(0, 0, 0)
-                forklift.bot.right_led.set_color(0, 0, 0)
+                forklift.alvik.left_led.set_color(0, 0, 0)
+                forklift.alvik.right_led.set_color(0, 0, 0)
                 forklift.lower_fork()
                 current_state = STATE_ALIGN
 
@@ -132,7 +132,7 @@ try:
         # ------------------------------------------------------------------
         elif current_state == STATE_RETURN_SPIN:
             forklift.log_info("Spinning 180...")
-            forklift.bot.rotate(180)
+            forklift.alvik.rotate(180)
             current_state = STATE_RETURN_DRIVE
 
         # ------------------------------------------------------------------
@@ -159,8 +159,8 @@ try:
         # ------------------------------------------------------------------
         elif current_state == STATE_SUCCESS:
             forklift.log_info("MISSION COMPLETE")
-            forklift.bot.left_led.set_color(0, 1, 0)
-            forklift.bot.right_led.set_color(0, 1, 0)
+            forklift.alvik.left_led.set_color(0, 1, 0)
+            forklift.alvik.right_led.set_color(0, 1, 0)
             time.sleep(3)
             current_state = STATE_IDLE
 
@@ -169,8 +169,8 @@ try:
         # ------------------------------------------------------------------
         elif current_state == STATE_FAIL:
             forklift.log_error("MISSION FAILED")
-            forklift.bot.left_led.set_color(1, 0, 0)
-            forklift.bot.right_led.set_color(1, 0, 0)
+            forklift.alvik.left_led.set_color(1, 0, 0)
+            forklift.alvik.right_led.set_color(1, 0, 0)
             time.sleep(3)
             current_state = STATE_IDLE
         
@@ -181,9 +181,9 @@ except KeyboardInterrupt:
 except Exception as e:
     forklift.log_error(f"Critical Error: {e}")
 finally:
-    forklift.bot.stop()
-    forklift.bot.left_led.set_color(0, 0, 0)
-    forklift.bot.right_led.set_color(0, 0, 0)
+    forklift.alvik.stop()
+    forklift.alvik.left_led.set_color(0, 0, 0)
+    forklift.alvik.right_led.set_color(0, 0, 0)
     forklift.log_info("Program terminated.")
 
 # Developed with the assistance of Google Gemini
\ No newline at end of file
