# Library: Alvik Web Controller
# Features: Graphical UI (File Based), Bitmasking, Analog Triggers, WebSockets
#
# Version: V11.0
# FIX: 'controller.html' path is now relative to this script.
#      This solves the "FileNotFound" error when running from root while files are in /lib.
# FIX: time.ticks_ms() rollover safety, network race condition, sequence traps, and ghost inputs.
# FIX: Replaced HTTP polling with WebSockets and binary payload unpacking for extreme low-latency.

import network
import socket
import select
import time
import binascii
import hashlib
import struct

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
        
        # Track time in integer milliseconds to prevent float/int crash in ticks_diff
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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', 80))
        self.server_socket.listen(1)
        self.server_socket.setblocking(False) # Non-blocking mode

        self.ws_client = None

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
        elapsed = time.ticks_diff(time.ticks_ms(), self.last_packet_time)
        time_ok = elapsed < 1000 
        return time_ok and self.connected

    def _check_verbose(self):
        if self.verbose:
            print(f"L:({self.left_x:.2f}, {self.left_y:.2f}) R:({self.right_x:.2f}, {self.right_y:.2f}) Btn:{self.buttons['cross']}")

    def _close_ws(self):
        if self.ws_client:
            try:
                self.ws_client.close()
            except:
                pass
            self.ws_client = None
        self.connected = False
        self._reset_state()
        if self.verbose: print("WebSocket Closed.")

    def _handle_http_req(self, req, cl):
        req_line = req.decode().split('\r\n')[0]

        # Serve UI
        if req_line.startswith('GET / HTTP'):
            cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n')
            cl.send(self.html)
            cl.close()
            return
            
        # Handle WebSocket Upgrade
        if req_line.startswith('GET /ws '):
            headers = req.decode().split('\r\n')
            key = None
            for h in headers:
                if h.lower().startswith('sec-websocket-key:'):
                    key = h.split(':')[1].strip()
                    break
            
            if key:
                # WebSocket Handshake
                magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                accept_key = binascii.b2a_base64(hashlib.sha1((key + magic).encode()).digest())[:-1].decode()
                
                resp = (
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
                )
                cl.send(resp.encode())
                cl.setblocking(False)
                
                # Close existing WS if any
                if self.ws_client:
                    self._close_ws()

                self.ws_client = cl
                self.last_packet_time = time.ticks_ms()
                self.connected = True
                if self.verbose: print("WebSocket Connected!")
            else:
                cl.close()
            return
            
        cl.close()

    def update(self):
        """Main server loop to be called in the main loop."""
        
        # Safety wipe: clear ghost inputs if the connection drops
        if not self.is_connected():
            self._reset_state()

        # Handle existing WebSocket connection
        if self.ws_client:
            r, _, _ = select.select([self.ws_client], [], [], 0)
            if r:
                try:
                    header = self.ws_client.recv(2)
                    if not header:
                        self._close_ws()
                        return

                    is_final = header[0] & 0x80
                    opcode = header[0] & 0x0f

                    if opcode == 8: # Close frame
                        self._close_ws()
                        return

                    is_masked = header[1] & 0x80
                    payload_len = header[1] & 0x7f

                    if payload_len == 126:
                        ext_len = self.ws_client.recv(2)
                        payload_len = struct.unpack(">H", ext_len)[0]
                    elif payload_len == 127:
                        ext_len = self.ws_client.recv(8)
                        payload_len = struct.unpack(">Q", ext_len)[0]

                    if is_masked:
                        mask = self.ws_client.recv(4)

                    payload = self.ws_client.recv(payload_len)

                    if opcode == 2 and is_masked and payload_len == 28: # Binary Frame size 28 (6 floats = 24 bytes + 1 uint32 = 4 bytes)
                        # Unmask
                        unmasked = bytearray(payload_len)
                        for i in range(payload_len):
                            unmasked[i] = payload[i] ^ mask[i % 4]

                        # Unpack 6 floats and 1 uint32
                        lx, ly, rx, ry, l2, r2, btn_mask = struct.unpack('<ffffffI', unmasked)

                        self.left_x = lx
                        self.left_y = ly
                        self.right_x = rx
                        self.right_y = ry
                        self.L2 = l2
                        self.R2 = r2

                        btn_names = ['cross', 'circle', 'square', 'triangle', 'L1', 'R1', 'L2', 'R2',
                                     'share', 'options', 'L3', 'R3', 'up', 'down', 'left', 'right', 'ps']

                        for i, name in enumerate(btn_names):
                            self.buttons[name] = bool((btn_mask >> i) & 1)

                        self.last_packet_time = time.ticks_ms()
                        self.connected = True
                        self._check_verbose()
                except OSError:
                    self._close_ws()

        # Non-blocking check for new connections
        r, _, _ = select.select([self.server_socket], [], [], 0)
        
        if r:
            try:
                cl, _ = self.server_socket.accept()
                cl.settimeout(0.5)
                try:
                    req = cl.recv(1024)
                    if req:
                        self._handle_http_req(req, cl)
                    else:
                        cl.close()
                except OSError:
                    cl.close()
            except OSError:
                pass
