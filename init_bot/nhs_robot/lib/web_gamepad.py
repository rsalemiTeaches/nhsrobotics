import network
import socket
import time
from arduino_alvik import ArduinoAlvik

class WebGamepad:
    def __init__(self, ssid="Alvik-RC", password="password123"):
        self.ssid = ssid
        self.password = password
        self.ip_address = "0.0.0.0"
        
        # --- Controller State ---
        # Axes are -100 to 100
        self.axes = [0, 0, 0, 0] # LX, LY, RX, RY
        # Buttons is a bitmask (integer) where each bit is a button
        self.buttons = 0
        
        # --- Mapping for standard gamepad ---
        self.BTN_A = 0
        self.BTN_B = 1
        self.BTN_X = 2
        self.BTN_Y = 3
        self.BTN_LB = 4
        self.BTN_RB = 5
        self.BTN_LT = 6
        self.BTN_RT = 7
        self.BTN_SELECT = 8
        self.BTN_START = 9
        self.BTN_L3 = 10
        self.BTN_R3 = 11
        self.BTN_UP = 12
        self.BTN_DOWN = 13
        self.BTN_LEFT = 14
        self.BTN_RIGHT = 15

        # --- Setup Networking ---
        self._setup_wifi()
        self._setup_server()

    def _setup_wifi(self):
        # Only set up WiFi if we aren't already connected
        self.ap = network.WLAN(network.AP_IF)
        if not self.ap.active():
            print(f"Creating WiFi: {self.ssid}...")
            self.ap.config(essid=self.ssid, password=self.password)
            self.ap.active(True)
            while not self.ap.active():
                time.sleep(0.1)
        
        self.ip_address = self.ap.ifconfig()[0]
        print(f"Success! Connect to {self.ssid}")
        print(f"Open Browser to: http://{self.ip_address}")

    def _setup_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # --- FIX FOR EADDRINUSE ERROR ---
        # This option allows us to reuse the port immediately after stopping
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.socket.bind(('', 80))
        self.socket.listen(5)
        self.socket.setblocking(False)

    def update(self):
        """
        Call this in your main loop! 
        It checks for new data from the phone/computer.
        """
        try:
            conn, addr = self.socket.accept()
            request = conn.recv(1024)
            req_str = str(request)

            # 1. Serve the Interface
            if "GET / " in req_str or "GET /index" in req_str:
                self._send_html(conn)
            
            # 2. Process Data Packet
            # Format: GET /data?ax=0,0,0,0&btn=12
            elif "GET /data" in req_str:
                self._parse_data(req_str)
                conn.send('HTTP/1.1 200 OK\n\n')
            
            conn.close()
        except OSError:
            pass # No new connection
        except Exception as e:
            print(f"Net Error: {e}")

    def _parse_data(self, req_str):
        try:
            # Extract "ax=0,0,0,0&btn=12"
            if '?' in req_str and ' ' in req_str:
                parts = req_str.split(' ')[1].split('?')[1]
                pairs = parts.split('&')
                
                for p in pairs:
                    key, val = p.split('=')
                    
                    if key == 'ax':
                        # val is "0,0,0,0"
                        ax_vals = val.split(',')
                        for i in range(4):
                            self.axes[i] = int(ax_vals[i])
                            
                    if key == 'btn':
                        self.buttons = int(val)
                    
        except Exception:
            pass

    def _send_html(self, conn):
        conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n')
        conn.sendall(self.HTML_CODE)

    # --- Student Methods ---

    def get_axis(self, index):
        """Returns axis value from -100 to 100"""
        if 0 <= index < 4:
            return self.axes[index]
        return 0

    def is_pressed(self, button_index):
        """Returns True if the button is held down"""
        mask = 1 << button_index
        return (self.buttons & mask) > 0

    # The secret sauce: Full Gamepad JS Interface
    HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<style>
body { background: #111; color: #eee; font-family: sans-serif; text-align: center; touch-action: none; }
.box { border: 1px solid #444; padding: 20px; margin: 10px; border-radius: 10px;}
h1 { color: #0f0; }
</style>
</head>
<body>
<h1>Alvik Connected</h1>
<div class="box">
    Status: <span id="stat">Waiting...</span><br>
    <small>Press any button to wake controller</small>
</div>
<div class="box" id="debug">No Data</div>

<script>
let lastQuery = "";

function loop() {
    const gps = navigator.getGamepads();
    const gp = gps[0];
    
    if(gp) {
        document.getElementById("stat").innerText = gp.id;
        
        // 1. Read Axes (Standard Layout)
        // 0: Left X, 1: Left Y, 2: Right X, 3: Right Y
        let ax = [];
        for(let i=0; i<4; i++) {
            // Scale -1.0 -> 1.0 to -100 -> 100
            let val = Math.round(gp.axes[i] * 100);
            if(Math.abs(val) < 10) val = 0; // Deadzone
            ax.push(val);
        }
        
        // 2. Read Buttons (Bitmask)
        let btnMask = 0;
        for(let i=0; i<16; i++) {
            if(gp.buttons[i] && gp.buttons[i].pressed) {
                btnMask |= (1 << i);
            }
        }
        
        // 3. Send if changed
        let query = "ax=" + ax.join(",") + "&btn=" + btnMask;
        
        if(query !== lastQuery) {
            document.getElementById("debug").innerText = query;
            fetch("/data?" + query).catch(e=>{});
            lastQuery = query;
        }
    }
    requestAnimationFrame(loop);
}
loop();
</script>
</body>
</html>
"""