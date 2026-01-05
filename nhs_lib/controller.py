# Library: Alvik Web Controller
# Features: Graphical UI (File Based), Bitmasking, Analog Triggers
#
# Version: V10.1
# FIX: 'controller.html' path is now relative to this script.
#      This solves the "FileNotFound" error when running from root while files are in /lib.

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
        self.last_packet_time = -500.0
        self.connected = False

        
        # 17 Buttons
        self.buttons = {
            'cross': False, 'circle': False, 'square': False, 'triangle': False,
            'L1': False, 'R1': False, 'L2': False, 'R2': False,
            'share': False, 'options': False, 'L3': False, 'R3': False,
            'up': False, 'down': False, 'left': False, 'right': False,
            'ps': False
        }

        # Connection Safety
        
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

        # --- HTML PAGE (SMART FILE LOAD) ---
        # V10 Change: Determine path relative to this script
        self.html = ""
        
        # 1. Determine where this script (controller.py) lives
        try:
            # __file__ is 'lib/controller.py'
            base_path = __file__.rsplit('/', 1)[0] 
            file_path = f"{base_path}/controller.html"
        except:
            # Fallback if __file__ fails
            file_path = "controller.html"

        # 2. Try to open the file
        try:
            with open(file_path, 'r') as f:
                self.html = f.read()
                # Template Replacement
                self.html = self.html.replace('{{ssid}}', self.ssid)
                print(f"Controller: Loaded UI from {file_path}")
        except OSError:
            # Fallback: Try root if lib failed
            try:
                with open('controller.html', 'r') as f:
                    self.html = f.read()
                    self.html = self.html.replace('{{ssid}}', self.ssid)
                    print("Controller: Loaded UI from root")
            except OSError:
                print(f"ERROR: Could not find 'controller.html' in {file_path} or root.")
                self.html = "<h1>Error: controller.html missing. Check /lib folder!</h1>"

    def is_connected(self):
        """Returns True if a valid packet was received in the last 300.0 seconds (5 mins)."""
        return ((time.time() - self.last_packet_time) < 300.0) and self.connected

    def _check_verbose(self):
        if self.verbose:
            print(f"L:({self.left_stick_x:.2f}, {self.left_stick_y:.2f}) R:({self.right_stick_x:.2f}, {self.right_stick_y:.2f}) Btn:{self.buttons['cross']}")

    def parse_request(self, req):
        """Parses the URL parameters from the HTTP GET request."""
        try:
            req_line = req.decode().split('\r\n')[0]
            
            # Update Heartbeat on Home Page Load (GET / )
            if req_line.startswith('GET / '): 
                return "HOME"
            
            # If no '?' is found, we can't parse parameters
            if '?' not in req_line:
                return "UNKNOWN"
            
            # Mark connection as active immediately upon receiving data
            self.last_packet_time = time.time()
            self.connected = True
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
            