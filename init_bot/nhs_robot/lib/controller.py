# Library: Alvik Web Controller
# Version: V02
# Features: Bitmasking, Analog Triggers, Inverted Y-Axis, Verbose Toggle, Visual Debug
# Created with the help of Gemini Pro

import network
import socket
import select
import time

class Controller:
    def __init__(self, ssid="Alvik-Link", password="password", verbose=False):
        self.ssid = ssid
        self.password = password
        self.verbose = verbose
        
        # --- STATE VARIABLES ---
        
        # Joysticks (Float -1.0 to 1.0)
        self.left_stick_x = 0.0
        self.left_stick_y = 0.0
        self.right_stick_x = 0.0
        self.right_stick_y = 0.0
        
        # Analog Triggers (Float 0.0 to 1.0)
        self.L2 = 0.0
        self.R2 = 0.0
        
        # 17 Buttons (Dictionary of Booleans)
        self.buttons = {
            'cross': False, 'circle': False, 'square': False, 'triangle': False, # 0-3
            'L1': False, 'R1': False, 'L2': False, 'R2': False,                  # 4-7
            'share': False, 'options': False, 'L3': False, 'R3': False,          # 8-11
            'up': False, 'down': False, 'left': False, 'right': False,           # 12-15
            'ps': False                                                          # 16
        }
        
        # --- INTERNAL TRACKING ---
        self._last_buttons = self.buttons.copy()
        self._last_axes = {
            'left_stick_x': 0.0, 'left_stick_y': 0.0,
            'right_stick_x': 0.0, 'right_stick_y': 0.0,
            'L2': 0.0, 'R2': 0.0
        }
        
        # Networking
        self.ap = network.WLAN(network.AP_IF)
        self.socket = None
        
        # HTML/JS Code
        # V02 Update: Added visual button grid for debugging
        self.html = """
        <!DOCTYPE html>
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body { font-family: sans-serif; background: #222; color: #fff; text-align: center; }
            .box { padding: 20px; background: #444; margin: 20px auto; max-width: 400px; border-radius: 10px; }
            .active { background: #00AA00 !important; }
            td { padding: 5px 10px; }
            
            /* Grid for Buttons */
            .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; max-width: 400px; margin: 0 auto; }
            .btn { background: #555; padding: 10px; border-radius: 5px; font-size: 10px; text-transform: uppercase; }
            .pressed { background: #00FF00 !important; color: #000; font-weight: bold; }
          </style>
        </head>
        <body>
          <h1>""" + self.ssid + """</h1>
          <div id="status" class="box">Connect Controller + Press Button</div>
          
          <div class="box">
            <table>
              <tr><td>LY: <span id="ly">0</span></td><td>RY: <span id="ry">0</span></td></tr>
              <tr><td>L2: <span id="l2">0</span></td><td>R2: <span id="r2">0</span></td></tr>
            </table>
          </div>

          <div class="grid">
             <div id="btn0" class="btn">Cross</div>
             <div id="btn1" class="btn">Circle</div>
             <div id="btn2" class="btn">Square</div>
             <div id="btn3" class="btn">Tri</div>
             
             <div id="btn4" class="btn">L1</div>
             <div id="btn5" class="btn">R1</div>
             <div id="btn6" class="btn">L2</div>
             <div id="btn7" class="btn">R2</div>
             
             <div id="btn8" class="btn">Share</div>
             <div id="btn9" class="btn">Opt</div>
             <div id="btn10" class="btn">L3</div>
             <div id="btn11" class="btn">R3</div>
             
             <div id="btn12" class="btn">Up</div>
             <div id="btn13" class="btn">Down</div>
             <div id="btn14" class="btn">Left</div>
             <div id="btn15" class="btn">Right</div>
             
             <div id="btn16" class="btn" style="grid-column: span 4">PS Button</div>
          </div>

          <script>
            let interval = null;
            
            window.addEventListener("gamepadconnected", (e) => {
              document.getElementById("status").innerText = "Active!";
              document.getElementById("status").classList.add("active");
              if (!interval) interval = setInterval(sendData, 100);
            });

            window.addEventListener("gamepaddisconnected", (e) => {
               document.getElementById("status").innerText = "Disconnected";
               document.getElementById("status").classList.remove("active");
               clearInterval(interval);
               interval = null;
            });

            function sendData() {
              const gp = navigator.getGamepads()[0];
              if (!gp) return;

              // 1. Axes (Invert Y so Up is Positive)
              let lx = gp.axes[0];
              let ly = -gp.axes[1]; 
              let rx = gp.axes[2];
              let ry = -gp.axes[3]; 
              
              if (Math.abs(lx) < 0.1) lx = 0;
              if (Math.abs(ly) < 0.1) ly = 0;
              if (Math.abs(rx) < 0.1) rx = 0;
              if (Math.abs(ry) < 0.1) ry = 0;

              let l2 = gp.buttons[6].value;
              let r2 = gp.buttons[7].value;

              document.getElementById("ly").innerText = ly.toFixed(1);
              document.getElementById("ry").innerText = ry.toFixed(1);
              document.getElementById("l2").innerText = l2.toFixed(1);
              document.getElementById("r2").innerText = r2.toFixed(1);

              // 2. Button Bitmask & Visual Grid
              let mask = 0;
              for (let i = 0; i < gp.buttons.length; i++) {
                // Update Bitmask
                if (gp.buttons[i].pressed) {
                  mask += (1 << i);
                }
                
                // Update Visual Grid
                let btnEl = document.getElementById("btn" + i);
                if (btnEl) {
                    if (gp.buttons[i].pressed) {
                        btnEl.classList.add("pressed");
                    } else {
                        btnEl.classList.remove("pressed");
                    }
                }
              }

              // 3. Send
              fetch(`/update?ax=${lx.toFixed(2)},${ly.toFixed(2)},${rx.toFixed(2)},${ry.toFixed(2)}&tr=${l2.toFixed(2)},${r2.toFixed(2)}&mk=${mask}`)
                .catch(e => {});
            }
          </script>
        </body>
        </html>
        """

    def begin(self):
        print(f"WiFi: {self.ssid} / {self.password}")
        self.ap.active(True)
        self.ap.config(essid=self.ssid, password=self.password)
        while not self.ap.active(): time.sleep(0.1)
        print(f"IP: {self.ap.ifconfig()[0]}")
        
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(addr)
        self.socket.listen(1)

    def _check_verbose(self):
        """Internal Check: Toggles verbose on PS button press"""
        # Rising Edge Detection for PS Button
        if self.buttons['ps'] and not self._last_buttons['ps']:
            self.verbose = not self.verbose
            print(f"[Controller] Verbose Mode: {'ON' if self.verbose else 'OFF'}")
        
        self._last_buttons['ps'] = self.buttons['ps']
        
        if not self.verbose: return
        
        # Print Button Changes
        for key, val in self.buttons.items():
            if key == 'ps': continue 
            if val != self._last_buttons[key]:
                status = "PRESSED" if val else "RELEASED"
                print(f"[Controller] {key}: {status}")
                self._last_buttons[key] = val
        
        # Print Axis Changes
        current_axes = {
            'LY': self.left_stick_y, 'RY': self.right_stick_y,
            'LX': self.left_stick_x, 'RX': self.right_stick_x,
            'L2': self.L2, 'R2': self.R2
        }
        for key, val in current_axes.items():
            if abs(val - self._last_axes.get(key, 0)) > 0.01:
                print(f"[Controller] {key}: {val:.2f}")
                self._last_axes[key] = val

    def parse_request(self, request):
        try:
            req = request.decode('utf-8').split('\r\n')[0]
            if "GET / " in req: return "HOME"
            
            if "/update?" in req:
                params = req.split('?')[1].split(' ')[0].split('&')
                mask = 0
                for p in params:
                    key, val = p.split('=')
                    if key == 'ax':
                        vals = val.split(',')
                        self.left_stick_x  = float(vals[0])
                        self.left_stick_y  = float(vals[1])
                        self.right_stick_x = float(vals[2])
                        self.right_stick_y = float(vals[3])
                    if key == 'tr':
                        vals = val.split(',')
                        self.L2 = float(vals[0])
                        self.R2 = float(vals[1])
                    if key == 'mk':
                        mask = int(val)
                
                # Unpack Bitmask
                btn_names = ['cross', 'circle', 'square', 'triangle', 'L1', 'R1', 'L2', 'R2', 
                             'share', 'options', 'L3', 'R3', 'up', 'down', 'left', 'right', 'ps']
                
                for i, name in enumerate(btn_names):
                    self.buttons[name] = bool((mask >> i) & 1)
                
                self._check_verbose()
                return "DATA"
            return "UNKNOWN"
        except: return "ERROR"

    def update(self):
        r, _, _ = select.select([self.socket], [], [], 0)
        if r:
            try:
                cl, _ = self.socket.accept()
                req = cl.recv(1024)
                if self.parse_request(req) == "HOME":
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                    cl.send(self.html)
                else:
                    cl.send('HTTP/1.0 200 OK\r\n\r\n')
                cl.close()
            except: pass
            
