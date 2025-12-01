# Library: Alvik Web Controller
# Features: Graphical UI (File Based), Bitmasking, Analog Triggers
#
# Version: V09
# FIX: Moved HTML content to external 'controller.html' file.
# FIX: Added templating to replace '{{ssid}}' with actual name.
# FIX: Retained 300.0s (5 min) safety timeout.

import network
import socket
import select
import time

class Controller:
    # --- SINGLETON IMPLEMENTATION ---
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensures only one instance of Controller is ever created."""
        if cls._instance is None:
            cls._instance = super(Controller, cls).__new__(cls)
            cls._instance._initialized = False 
        return cls._instance

    def __init__(self, ssid="Alvik-Link", password="password", verbose=False):
        """Initializes the instance only if it hasn't been initialized before."""
        if self._initialized:
            return
            
        self.ssid = ssid
        self.password = password
        self.verbose = verbose
        
        # --- STATE VARIABLES ---
        self.left_stick_x = 0.0
        self.left_stick_y = 0.0
        self.right_stick_x = 0.0
        self.right_stick_y = 0.0
        self.L2 = 0.0
        self.R2 = 0.0
        
        # 17 Buttons
        self.buttons = {
            'cross': False, 'circle': False, 'square': False, 'triangle': False,
            'L1': False, 'R1': False, 'L2': False, 'R2': False,
            'share': False, 'options': False, 'L3': False, 'R3': False,
            'up': False, 'down': False, 'left': False, 'right': False, 'ps': False
        }

        # Connection Safety
        self.last_packet_time = 0
        
        # --- WIFI SETUP (AP MODE) ---
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid=self.ssid, password=self.password, authmode=3)

        while not self.ap.active():
            time.sleep(0.1)
            
        print(f"Controller: AP '{self.ssid}' Active. IP: {self.ap.ifconfig()[0]}")

        # --- SOCKET SETUP ---
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', 80))
        self.socket.listen(5)
        self.socket.setblocking(False) # Non-blocking mode

        self._initialized = True

        # --- HTML PAGE (FILE LOAD) ---
        # V09 Change: Read from external file instead of hardcoded string
        try:
            with open('controller.html', 'r') as f:
                self.html = f.read()
                # Template Replacement:
                # We look for {{ssid}} in the file and replace it with self.ssid
                self.html = self.html.replace('{{ssid}}', self.ssid)
        except OSError:
            print("ERROR: controller.html not found on device!")
            self.html = "<h1>Error: controller.html missing. Upload the file!</h1>"

    def is_connected(self):
        """Returns True if a valid packet was received in the last 300.0 seconds (5 mins)."""
        return (time.time() - self.last_packet_time) < 300.0

    def _check_verbose(self):
        if self.verbose:
            print(f"L:({self.left_stick_x:.2f}, {self.left_stick_y:.2f}) R:({self.right_stick_x:.2f}, {self.right_stick_y:.2f}) Btn:{self.buttons['cross']}")

    def parse_request(self, req):
        """Parses the URL parameters from the HTTP GET request."""
        try:
            req_line = req.decode().split('\r\n')[0]
            
            # Update Heartbeat on Home Page Load (GET / )
            if req_line.startswith('GET / '): 
                self.last_packet_time = time.time()
                return "HOME"
            
            # If no '?' is found, we can't parse parameters
            if '?' not in req_line:
                return "UNKNOWN"
            
            # Mark connection as active immediately upon receiving data
            self.last_packet_time = time.time()

            # Robustly extract query string: GET /update?ax=... HTTP/1.1
            url_part = req_line.split(' ')[1]
            query_string = url_part.split('?')[1]
            
            pairs = query_string.split('&')
            mask = 0
            
            for pair in pairs:
                if '=' not in pair: continue
                key, val = pair.split('=')
                
                # Axes logic matching the JS sender
                if key == 'ax':
                    vals = val.split(',')
                    if len(vals) == 4:
                        self.left_stick_x = float(vals[0])
                        self.left_stick_y = float(vals[1])
                        self.right_stick_x = float(vals[2])
                        self.right_stick_y = float(vals[3])

                # Triggers (L2, R2)
                if key == 'tr':
                    vals = val.split(',')
                    if len(vals) == 2:
                        self.L2 = float(vals[0])
                        self.R2 = float(vals[1])
                
                # Button Mask
                if key == 'mk':
                    mask = int(val)
            
            btn_names = ['cross', 'circle', 'square', 'triangle', 'L1', 'R1', 'L2', 'R2', 
                         'share', 'options', 'L3', 'R3', 'up', 'down', 'left', 'right', 'ps']
            
            for i, name in enumerate(btn_names):
                self.buttons[name] = bool((mask >> i) & 1)
            
            self._check_verbose()
            return "DATA"
        except Exception as e:
            if self.verbose: print(f"Parse Error: {e}")
            return "ERROR"

    def update(self):
        """Main server loop to be called in the main loop."""
        # Non-blocking check for new connections
        r, _, _ = select.select([self.socket], [], [], 0) 
        
        if r:
            try:
                cl, _ = self.socket.accept()
                req = cl.recv(1024)
                
                if req:
                    parse_result = self.parse_request(req)
                    
                    if parse_result == "HOME":
                        # Send HTML Header and Content
                        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                        cl.send(self.html)
                    else:
                        # Send Empty Success Response (Fast)
                        cl.send('HTTP/1.0 200 OK\r\n\r\n')
                        
                cl.close()
            except OSError:
                pass