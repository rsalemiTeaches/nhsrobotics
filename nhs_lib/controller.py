# Library: Alvik Web Controller
# Features: Graphical UI (File Based), Bitmasking, Analog Triggers, WebSockets
#
# Version: V11.2
# FIX: Buffer drain loop. Drains all stale WebSocket packets to eliminate queue latency.
# FIX: Added performance instrumentation (packets dropped counter).

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
        if cls._instance is None:
            cls._instance = super(Controller, cls).__new__(cls)
            cls._instance._initialized = False 
        return cls._instance

    def __init__(self, ssid="Alvik-Link", password="password", verbose=False, bot=None):
        if self._initialized:
            return
            
        self.ssid = ssid
        self.password = password
        self.verbose = verbose
        self.bot = bot
        
        # --- STATE VARIABLES ---
        self.left_x = 0.0
        self.left_y = 0.0
        self.right_x = 0.0
        self.right_y = 0.0
        self.L2 = 0.0
        self.R2 = 0.0
        
        self.last_packet_time = time.ticks_ms()
        self.connected = False
        
        self.buttons = {
            'cross': False, 'circle': False, 'square': False, 'triangle': False,
            'L1': False, 'R1': False, 'L2': False, 'R2': False,
            'share': False, 'options': False, 'L3': False, 'R3': False,
            'up': False, 'down': False, 'left': False, 'right': False,
            'ps': False
        }
        
        # --- WIFI SETUP (AP MODE) ---
        self.ap = network.WLAN(network.AP_IF)
        if not self.ap.active():
            if self.bot and hasattr(self.bot, "log_info"): self.bot.log_info(f"Starting AP: {self.ssid}")
            self.ap.active(True)
            self.ap.config(essid=self.ssid, password=self.password, authmode=3)

            while not self.ap.active():
                time.sleep(0.1)
            
        msg = f"AP Ready: {self.ap.ifconfig()[0]}"
        if self.bot and hasattr(self.bot, "log_info"): self.bot.log_info(msg)
        print("Controller:", msg)

        # --- SOCKET SETUP ---
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', 80))
        self.server_socket.listen(1)
        self.server_socket.setblocking(False)

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
        except OSError:
            try:
                with open('controller.html', 'r') as f:
                    self.html = f.read()
                    self.html = self.html.replace('{{ssid}}', self.ssid)
            except OSError:
                if self.bot and hasattr(self.bot, "log_info"): self.bot.log_info("Error: HTML missing!")
                self.html = "<h1>Error: controller.html missing. Check /lib folder!</h1>"

    def _reset_state(self):
        self.left_x, self.left_y = 0.0, 0.0
        self.right_x, self.right_y = 0.0, 0.0
        self.L2, self.R2 = 0.0, 0.0
        for key in self.buttons:
            self.buttons[key] = False

    def is_connected(self):
        elapsed = time.ticks_diff(time.ticks_ms(), self.last_packet_time)
        time_ok = elapsed < 1000 
        return time_ok and self.connected

    def _close_ws(self):
        if self.ws_client:
            try:
                self.ws_client.close()
            except:
                pass
            self.ws_client = None
        if self.connected:
            self.connected = False
            self._reset_state()
            if self.bot and hasattr(self.bot, "log_info"): self.bot.log_info("WS Closed/Dropped")

    def _read_exact(self, sock, n):
        data = bytearray()
        timeout_start = time.ticks_ms()
        while len(data) < n:
            if time.ticks_diff(time.ticks_ms(), timeout_start) > 200:
                raise OSError("WS Read Timeout")
            try:
                r, _, _ = select.select([sock], [], [], 0.01)
                if r:
                    chunk = sock.recv(n - len(data))
                    if not chunk:
                        raise OSError("WS Socket Closed")
                    data.extend(chunk)
            except OSError as e:
                if e.args[0] != 11:
                    raise e
        return bytes(data)

    def _handle_http_req(self, req, cl):
        req_line = req.decode().split('\r\n')[0]

        if req_line.startswith('GET / HTTP'):
            cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n')
            cl.send(self.html)
            cl.close()
            if self.bot and hasattr(self.bot, "log_info"): self.bot.log_info("Served UI")
            return
            
        if req_line.startswith('GET /ws '):
            headers = req.decode().split('\r\n')
            key = None
            for h in headers:
                if h.lower().startswith('sec-websocket-key:'):
                    key = h.split(':')[1].strip()
                    break
            
            if key:
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
                
                if self.ws_client:
                    self._close_ws()

                self.ws_client = cl
                self.last_packet_time = time.ticks_ms()
                self.connected = True
                if self.bot and hasattr(self.bot, "log_info"): self.bot.log_info("WS Connected!")
            else:
                cl.close()
            return
            
        cl.close()

    def update(self):
        if not self.is_connected():
            self._reset_state()

        if self.ws_client:
            packets_processed = 0
            # Buffer Drain Loop: Read until socket is empty
            while True:
                r, _, _ = select.select([self.ws_client], [], [], 0)
                if not r:
                    break # No more data in buffer

                try:
                    header = self._read_exact(self.ws_client, 2)

                    is_final = header[0] & 0x80
                    opcode = header[0] & 0x0f

                    if opcode == 8:
                        if self.bot and hasattr(self.bot, "log_info"): self.bot.log_info("WS Graceful Close")
                        self._close_ws()
                        return

                    is_masked = header[1] & 0x80
                    payload_len = header[1] & 0x7f

                    if payload_len == 126:
                        ext_len = self._read_exact(self.ws_client, 2)
                        payload_len = struct.unpack(">H", ext_len)[0]
                    elif payload_len == 127:
                        ext_len = self._read_exact(self.ws_client, 8)
                        payload_len = struct.unpack(">Q", ext_len)[0]

                    if is_masked:
                        mask = self._read_exact(self.ws_client, 4)

                    if payload_len > 0:
                        payload = self._read_exact(self.ws_client, payload_len)
                    else:
                        payload = b''

                    if opcode == 2 and is_masked and payload_len == 28:
                        unmasked = bytearray(payload_len)
                        for i in range(payload_len):
                            unmasked[i] = payload[i] ^ mask[i % 4]

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
                        packets_processed += 1
                except OSError as e:
                    if self.bot and hasattr(self.bot, "log_info"): self.bot.log_info(f"WS Err: {e}")
                    self._close_ws()
                    break

            # Instrumentation: Log if we had to drop stale packets
            if packets_processed > 1:
                # We processed more than 1 packet this cycle.
                # Only the last one matters. The others were stale.
                dropped = packets_processed - 1
                if self.bot and hasattr(self.bot, "log_info"): self.bot.log_info(f"Lag Drop: {dropped} pkts")

        # Accept new connections
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
