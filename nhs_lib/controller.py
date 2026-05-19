# Library: Alvik Web Controller
# Features: Graphical UI (File Based), Bitmasking, Analog Triggers
#
# Version: V10.2
# FIX: 'controller.html' path is now relative to this script.
#      This solves the "FileNotFound" error when running from root while files are in /lib.
# FIX: time.ticks_ms() rollover safety, network race condition, sequence traps, and ghost inputs.

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
        self.left_x = 0.0
        self.left_y = 0.0
        self.right_x = 0.0
        self.right_y = 0.0
        self.L2 = 0.0
        self.R2 = 0.0
        
        # FIX: Track time in integer milliseconds to prevent float/int crash in ticks_diff
        self.last_packet_time = time.ticks_ms()
        self.connected = False
        
        # 17 Buttons
        self.buttons = {
            'cross': False, 'circle': False, 'square': False, 'triangle': False,
            'L1': False, 'R1': False, 'L2': False, 'R2': False,
            'share': False, 'options': False, 'L3': False, 'R3': False,
            'up': False, 'down': False, 'left': False, 'right': False,
            'ps': False
        }
        
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
        self.html = ""
        
        try:
            base_path = __file__.rsplit('/', 1)[0] 
            file_path = f"{base_path}/controller.html"
        except:
            file_path = "controller.html"

        try:
            with open(file_path, 'r') as f:
                self.html = f.read()
                self.html = self.html.replace('{{ssid}}', self.ssid)
                print(f"Controller: Loaded UI from {file_path}")
        except OSError:
            try:
                with open('controller.html', 'r') as f:
                    self.html = f.read()
                    self.html = self.html.replace('{{ssid}}', self.ssid)
                    print("Controller: Loaded UI from root")
            except OSError:
                print(f"ERROR: Could not find 'controller.html' in {file_path} or root.")
                self.html = "<h1>Error: controller.html missing. Check /lib folder!</h1>"

    def _reset_state(self):
        """Zeros out all inputs if connection is lost to prevent runaway robots."""
        self.left_x, self.left_y = 0.0, 0.0
        self.right_x, self.right_y = 0.0, 0.0
        self.L2, self.R2 = 0.0, 0.0
        for key in self.buttons:
            self.buttons[key] = False

    def is_connected(self):
        """Returns True if a valid packet was received in the last 1000ms."""
        # Calculate milliseconds passed, accounting for hardware clock rollover
        elapsed = time.ticks_diff(time.ticks_ms(), self.last_packet_time)
        # 1000ms gives plenty of padding for the HTML 250ms heartbeat over Wi-Fi
        time_ok = elapsed < 1000 
        return time_ok and self.connected

    def _check_verbose(self):
        if self.verbose:
            print(f"L:({self.left_x:.2f}, {self.left_y:.2f}) R:({self.right_x:.2f}, {self.right_y:.2f}) Btn:{self.buttons['cross']}")

    def parse_request(self, req):
        """Parses the URL parameters from the HTTP GET request."""
        try:
            req_line = req.decode().split('\r\n')[0]
            
            # Mark connection as active FIRST so initial page loads register correctly
            self.last_packet_time = time.ticks_ms()
            self.connected = True           
            
            # Update Heartbeat on Home Page Load (GET / )
            if req_line.startswith('GET / '): 
                return "HOME"
            
            # If no '?' is found, we can't parse parameters
            if '?' not in req_line:
                return "UNKNOWN"
            
            # Robustly extract query string: GET /update?ax=... HTTP/1.1
            url_part = req_line.split(' ')[1]
            query_string = url_part.split('?')[1]
            pairs = query_string.split('&')
            mask = 0
            
            for pair in pairs:
                if '=' not in pair: continue
                key, val = pair.split('=')
                
                if key == 'ax':
                    vals = val.split(',')
                    if len(vals) == 4:
                        self.left_x = float(vals[0])
                        self.left_y = float(vals[1])
                        self.right_x = float(vals[2])
                        self.right_y = float(vals[3])

                if key == 'tr':
                    vals = val.split(',')
                    if len(vals) == 2:
                        self.L2 = float(vals[0])
                        self.R2 = float(vals[1])
                
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
        
        # Safety wipe: clear ghost inputs if the connection drops
        if not self.is_connected():
            self._reset_state()

        # Non-blocking check for new connections
        r, _, _ = select.select([self.socket], [], [], 0) 
        
        if r:
            try:
                cl, _ = self.socket.accept()
                cl.settimeout(0.1) # Prevent server from hanging on recv
                try:
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
                except OSError:
                    # Timeout or disconnect during recv
                    pass
                finally:
                    cl.close()
            except OSError:
                pass