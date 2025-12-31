# Project 17: The Web RC Car (Mobile + Chromebook Edition)
#
# GOAL:
# 1. Host a Website that supports BOTH Gamepads and Touchscreens.
# 2. Use 'ontouchstart' to drive while holding a button.
# 3. Stop immediately when the button is released.

import network
import socket
import json
from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# --- Configuration ---
SSID = "Alvik-RC"
PASSWORD = "password123"

print("Starting Project 17: Mobile RC...")
alvik = ArduinoAlvik()
alvik.begin()

# --- 1. Create WiFi Hotspot ---
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

while not ap.active():
    pass

ip = ap.ifconfig()[0]
print(f"WiFi Created: {SSID}")
print(f"Go to URL: http://{ip}")

# --- 2. The Mobile-Friendly Website ---
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Alvik Mobile</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
    <style>
        body { 
            font-family: sans-serif; 
            text-align: center; 
            background: #222; 
            color: #fff;
            touch-action: none; /* Prevents scrolling while driving */
            user-select: none;  /* Prevents highlighting text */
        }
        h1 { margin-bottom: 5px; color: #00ff00; }
        
        /* Grid layout for the D-Pad */
        .control-grid {
            display: grid;
            grid-template-columns: 100px 100px 100px;
            grid-template-rows: 100px 100px 100px;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
        }
        
        .btn {
            background: #444;
            border: 2px solid #666;
            border-radius: 15px;
            color: white;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn:active { background: #00ff00; color: black; border-color: #fff; }
        
        /* Button Positioning */
        .up    { grid-column: 2; grid-row: 1; background: #005500; }
        .left  { grid-column: 1; grid-row: 2; background: #555500; }
        .stop  { grid-column: 2; grid-row: 2; background: #550000; }
        .right { grid-column: 3; grid-row: 2; background: #555500; }
        .down  { grid-column: 2; grid-row: 3; background: #005500; }
        
        .status-box { margin-top: 20px; font-size: 14px; color: #aaa; }
    </style>
</head>
<body>
    <h1>Alvik Remote</h1>
    
    <div class="control-grid">
        <!-- Touch Buttons -->
        <!-- onpointerdown handles both Mouse Clicks AND Touch Taps -->
        <div class="btn up"    onpointerdown="drive(60, 60)"   onpointerup="stop()" onpointerleave="stop()">▲</div>
        <div class="btn left"  onpointerdown="drive(-50, 50)"  onpointerup="stop()" onpointerleave="stop()">◀</div>
        <div class="btn stop"  onpointerdown="stop()">STOP</div>
        <div class="btn right" onpointerdown="drive(50, -50)"  onpointerup="stop()" onpointerleave="stop()">▶</div>
        <div class="btn down"  onpointerdown="drive(-60, -60)" onpointerup="stop()" onpointerleave="stop()">▼</div>
    </div>

    <div class="status-box">
        Works with Touch OR Gamepad<br>
        Last Command: <span id="debug">None</span>
    </div>

    <script>
        // --- TOUCH LOGIC ---
        function drive(l, r) {
            sendDrive(l, r);
            document.getElementById('debug').innerText = "L:" + l + " R:" + r;
        }

        function stop() {
            sendDrive(0, 0);
            document.getElementById('debug').innerText = "STOP";
        }

        function sendDrive(l, r) {
            fetch('/drive?l=' + l + '&r=' + r).catch(e => console.log(e));
        }

        // --- GAMEPAD LOGIC (Background) ---
        let gpLastL = 0;
        let gpLastR = 0;

        function gamepadLoop() {
            const gamepads = navigator.getGamepads();
            const gp = gamepads[0];

            if (gp) {
                // Only override touch if the joystick is actually moved
                let rawL = gp.axes[1]; 
                let rawR = gp.axes[3]; 
                let speedL = Math.round(rawL * -80);
                let speedR = Math.round(rawR * -80);

                if (Math.abs(speedL) < 10) speedL = 0;
                if (Math.abs(speedR) < 10) speedR = 0;

                // Only send if values changed significantly
                if (speedL !== gpLastL || speedR !== gpLastR) {
                    sendDrive(speedL, speedR);
                    gpLastL = speedL;
                    gpLastR = speedR;
                    document.getElementById('debug').innerText = "Gamepad Active";
                }
            }
            requestAnimationFrame(gamepadLoop);
        }
        gamepadLoop();
    </script>
</body>
</html>
"""

# --- 3. Start Web Server ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
s.setblocking(False)

print("Mobile Server Listening...")
alvik.left_led.set_color(0, 0, 1) # Blue = Ready

try:
    while not alvik.get_touch_cancel():
        try:
            conn, addr = s.accept()
            request = conn.recv(1024)
            req_str = str(request)
            
            if "GET / " in req_str or "GET /index" in req_str:
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Connection: close\n\n')
                conn.sendall(html_page)
                
            elif "GET /drive" in req_str:
                try:
                    # Parse /drive?l=50&r=50
                    parts = req_str.split(' ')[1]
                    params = parts.split('?')[1]
                    pairs = params.split('&')
                    l_speed = 0
                    r_speed = 0
                    for p in pairs:
                        key, val = p.split('=')
                        if key == 'l': l_speed = int(val)
                        if key == 'r': r_speed = int(val)
                    
                    alvik.set_wheels_speed(l_speed, r_speed)
                    conn.send('HTTP/1.1 200 OK\n\n')
                except:
                    pass
            
            conn.close()
        except OSError:
            pass
            
except Exception as e:
    print(e)

finally:
    alvik.stop()
    alvik.set_wheels_speed(0, 0)