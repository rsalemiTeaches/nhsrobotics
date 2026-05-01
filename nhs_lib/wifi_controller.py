# wifi_controller.py
# Version: V50 (Non-Blocking, Throttled, Dictionary-Mapped)
#
# A highly robust, non-blocking web server for Gamepad control.
# Features:
# - Client-side bandwidth throttling (sends data only on change)
# - 250ms Heartbeat to maintain connection state
# - 500ms "Runaway Robot" safety timeout
# - Complete 16-button dictionary mapping and 4-axis support

import network
import socket
import select
import time


class Controller:
    """
    Manages a non-blocking Wi-Fi Access Point and Web Server to 
    receive standard Gamepad API data from a connected client.
    """

    def __init__(self, ssid="Alvik-Link", password="password"):
        self.ssid = ssid
        self.password = password

        # --- Gamepad State Variables ---
        self.left_x = 0
        self.left_y = 0
        self.right_x = 0
        self.right_y = 0

        # Dictionary maps standard HTML5 gamepad buttons (PlayStation style)
        self.buttons = {
            'cross': False, 'circle': False, 'square': False, 'triangle': False,
            'L1': False, 'R1': False, 'L2': False, 'R2': False,
            'share': False, 'options': False, 'L3': False, 'R3': False,
            'up': False, 'down': False, 'left': False, 'right': False
        }

        # --- Internal State ---
        self.last_packet_time = 0
        self.timeout_ms = 500

        self.ap = None
        self.socket = None

        # Automatically start the network on creation
        self._setup_wifi()
        self._setup_server()

    def _setup_wifi(self):
        """Initializes the ESP32 Access Point."""
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid=self.ssid, password=self.password, authmode=network.AUTH_WPA_WPA2_PSK)
        # Wait briefly for AP to spin up
        while not self.ap.active():
            time.sleep_ms(100)

    def _setup_server(self):
        """Initializes the non-blocking socket server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', 80))
        self.socket.listen(1)

    def is_connected(self):
        """
        Returns True if a packet has been received within the timeout window.
        Acts as the primary safety check for 'Runaway Robot' prevention.
        """
        if self.last_packet_time == 0:
            return False
        return time.ticks_diff(time.ticks_ms(), self.last_packet_time) < self.timeout_ms

    def _reset_state(self):
        """Zeros out all inputs. Called when the connection times out."""
        self.left_x = 0
        self.left_y = 0
        self.right_x = 0
        self.right_y = 0
        for key in self.buttons:
            self.buttons[key] = False

    def update(self):
        """
        MUST be called in the main loop.
        Checks for timeouts and quickly drains the socket of any new data.
        """
        # 1. Safety Timeout: Kill inputs if we lost the connection
        if not self.is_connected():
            self._reset_state()

        # 2. Non-blocking check for incoming socket data
        # r = ready to read, w = ready to write, e = errors
        r, w, e = select.select([self.socket], [], [], 0)

        if r:
            try:
                # Accept connection and set a tiny timeout so recv doesn't hang
                cl, addr = self.socket.accept()
                cl.settimeout(0.1)
                request = cl.recv(1024).decode('utf-8')

                if 'GET / ' in request or ('GET /?' not in request and 'GET' in request):
                    # Client wants the webpage HTML
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                    cl.send(self._get_html())
                elif 'GET /?ax=' in request:
                    # Client is sending telemetry data
                    self._parse_data(request)
                    cl.send('HTTP/1.0 200 OK\r\n\r\n')

                cl.close()
            except Exception:
                # Catch timeout or OS errors quietly and move on
                pass

    def _parse_data(self, request):
        """Parses the lightweight query string (e.g., /?ax=0,100,0,0&b=32)"""
        try:
            # Extract just the data string between the target and HTTP protocol
            start = request.find('/?ax=') + 5
            end = request.find(' HTTP')
            data_str = request[start:end]
            
            # Split axes and buttons
            ax_str, b_str = data_str.split('&b=')
            ax_vals = ax_str.split(',')

            # Update Axes
            self.left_x = int(ax_vals[0])
            self.left_y = int(ax_vals[1])
            self.right_x = int(ax_vals[2])
            self.right_y = int(ax_vals[3])

            # Update Buttons (Bitmask decoding)
            bitmask = int(b_str)
            self.buttons['cross']    = bool(bitmask & (1 << 0))
            self.buttons['circle']   = bool(bitmask & (1 << 1))
            self.buttons['square']   = bool(bitmask & (1 << 2))
            self.buttons['triangle'] = bool(bitmask & (1 << 3))
            self.buttons['L1']       = bool(bitmask & (1 << 4))
            self.buttons['R1']       = bool(bitmask & (1 << 5))
            self.buttons['L2']       = bool(bitmask & (1 << 6))
            self.buttons['R2']       = bool(bitmask & (1 << 7))
            self.buttons['share']    = bool(bitmask & (1 << 8))
            self.buttons['options']  = bool(bitmask & (1 << 9))
            self.buttons['L3']       = bool(bitmask & (1 << 10))
            self.buttons['R3']       = bool(bitmask & (1 << 11))
            self.buttons['up']       = bool(bitmask & (1 << 12))
            self.buttons['down']     = bool(bitmask & (1 << 13))
            self.buttons['left']     = bool(bitmask & (1 << 14))
            self.buttons['right']    = bool(bitmask & (1 << 15))

            # Register heartbeat to keep is_connected() True
            self.last_packet_time = time.ticks_ms()
        except Exception:
            pass

    def _get_html(self):
        """
        Returns the HTML/JS payload. 
        Note: The JavaScript handles bandwidth throttling and Y-axis inversion.
        """
        return """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
    <title>Alvik Controller</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; text-align: center; margin-top: 50px; }
        .box { padding: 20px; background: #333; border-radius: 10px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h1 { color: #00ffcc; margin-bottom: 5px;}
    </style>
</head>
<body>
    <div class="box">
        <h1>Alvik Link Active</h1>
        <p id="st">Press any button on controller to wake.</p>
    </div>
    <script>
        let q = "";
        let t = 0;
        let s = false;
        
        setInterval(() => {
            const gps = navigator.getGamepads();
            const gp = gps[0];
            if(!gp) return;
            
            document.getElementById("st").innerText = "Transmitting: " + gp.id;
            
            // 1. Parse Axes (Invert Y axes for standard robotics logic)
            let ax = [];
            for(let i=0; i<4; i++) {
                let v = Math.round(gp.axes[i] * 100);
                if(Math.abs(v) < 10) v = 0; // Deadzone
                if(i === 1 || i === 3) v = -v; // Invert Y
                ax.push(v);
            }
            
            // 2. Parse Buttons to Bitmask
            let b = 0;
            for(let i=0; i<16; i++) {
                if(gp.buttons[i] && gp.buttons[i].pressed) {
                    b |= (1 << i);
                }
            }
            
            // 3. Bandwidth Throttling & Heartbeat
            let nq = ax.join(',') + "&b=" + b;
            let n = Date.now();
            
            // Send if data changed OR 250ms heartbeat elapsed (and not currently sending)
            if((nq !== q || n - t > 250) && !s) {
                s = true; 
                q = nq; 
                t = n;
                fetch("/?ax=" + nq)
                    .catch(e => {})
                    .finally(() => { s = false; });
            }
        }, 50); // Run at 20fps
    </script>
</body>
</html>"""
