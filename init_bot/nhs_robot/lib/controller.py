# Library: Alvik Web Controller
# Version: v02
# Features: Bitmasking, Analog Triggers, Inverted Y-Axis, Verbose Toggle
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
        
        # HTML/JS Code (Now includes full graphical debug interface)
        self.html = """
        <!DOCTYPE html>
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body { font-family: sans-serif; text-align: center; margin: 0; padding: 20px; background: #1f2937; color: #fff; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; background: #374151; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
            h1 { font-size: 1.5rem; margin-bottom: 5px; }
            #status { padding: 8px; background: #4b5563; border-radius: 8px; margin-bottom: 20px; font-weight: 600; }
            .active { background: #10b981 !important; }
            
            /* STICKS */
            .sticks-grid { display: flex; justify-content: space-around; gap: 20px; margin-bottom: 20px; }
            .stick-container { width: 100px; height: 100px; background: #4b5563; border-radius: 50%; position: relative; border: 2px solid #6b7280; margin: 0 auto; }
            .stick { width: 20px; height: 20px; background: #ef4444; border-radius: 50%; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); transition: transform 0.05s linear; box-shadow: 0 0 5px rgba(0,0,0,0.8); }
            
            /* TRIGGERS */
            .triggers-container { display: flex; justify-content: center; align-items: flex-end; gap: 40px; margin-bottom: 20px; }
            .meter-bar { width: 30px; height: 100px; background: #6b7280; border-radius: 5px; overflow: hidden; position: relative; }
            .meter-fill { position: absolute; bottom: 0; width: 100%; background: #3b82f6; transition: height 0.05s linear; }
            
            /* BUTTONS */
            .button-grid { 
                display: grid; 
                grid-template-columns: repeat(4, 1fr); 
                gap: 10px; 
                margin-top: 20px;
                grid-template-areas: 
                    "tri squ circ cross"
                    "l1 r1 l2 r2"
                    "share option l3 r3"
                    "dpad dpad dpad ps"; 
            }
            .button { padding: 10px 5px; background: #4b5563; border-radius: 6px; font-size: 0.8rem; transition: background 0.05s ease; user-select: none; }
            .active-btn { background: #facc15; color: #1f2937; font-weight: 700; box-shadow: 0 0 8px rgba(250, 204, 21, 0.7); }
            
            /* D-Pad specific adjustments for better layout */
            .dpad-wrapper { 
                grid-area: dpad; 
                display: grid; 
                grid-template-columns: repeat(3, 1fr); 
                grid-template-rows: repeat(3, 1fr); 
                gap: 2px;
                background: #4b5563;
                border-radius: 6px;
                padding: 5px;
            }
            .dpad-btn { 
                padding: 5px;
                background: #5a6474; /* Darker than regular button for contrast */
                border-radius: 3px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .dpad-center { visibility: hidden; } /* Placeholder for center of d-pad */
            
            #btn-triangle { grid-area: tri; }
            #btn-square { grid-area: squ; }
            #btn-circle { grid-area: circ; }
            #btn-cross { grid-area: cross; }
            #btn-L1 { grid-area: l1; }
            #btn-R1 { grid-area: r1; }
            #btn-L2 { grid-area: l2; }
            #btn-R2 { grid-area: r2; }
            #btn-share { grid-area: share; }
            #btn-options { grid-area: option; }
            #btn-L3 { grid-area: l3; }
            #btn-R3 { grid-area: r3; }
            #btn-ps { grid-area: ps; }

          </style>
        </head>
        <body>
          <div class="container">
            <h1>Controller Link: """ + self.ssid + """</h1>
            <div id="status">Waiting for Controller...</div>

            <!-- STICK DISPLAY -->
            <div class="sticks-grid">
              <div>
                <p>Left Stick (LY/LX)</p>
                <div class="stick-container"><div id="ls-pos" class="stick"></div></div>
              </div>
              <div>
                <p>Right Stick (RY/RX)</p>
                <div class="stick-container"><div id="rs-pos" class="stick"></div></div>
              </div>
            </div>

            <!-- TRIGGER DISPLAY -->
            <div class="triggers-container">
              <div>L2 Value (0.00)</div>
              <div class="meter-bar"><div id="l2-fill" class="meter-fill"></div></div>
              <div class="meter-bar"><div id="r2-fill" class="meter-fill"></div></div>
              <div>R2 Value (0.00)</div>
            </div>

            <!-- BUTTON DISPLAY -->
            <h2>Button Status</h2>
            <div class="button-grid" id="button-grid-container">
                <!-- Main Buttons -->
                <div class="button" id="btn-triangle">Triangle</div>
                <div class="button" id="btn-square">Square</div>
                <div class="button" id="btn-circle">Circle</div>
                <div class="button" id="btn-cross">Cross</div>

                <!-- Bumpers/Triggers (Digital) -->
                <div class="button" id="btn-L1">L1</div>
                <div class="button" id="btn-R1">R1</div>
                <div class="button" id="btn-L2">L2 (D)</div>
                <div class="button" id="btn-R2">R2 (D)</div>

                <!-- Options/Sticks -->
                <div class="button" id="btn-share">Share</div>
                <div class="button" id="btn-options">Options</div>
                <div class="button" id="btn-L3">L3 (Click)</div>
                <div class="button" id="btn-R3">R3 (Click)</div>

                <!-- D-Pad -->
                <div class="dpad-wrapper">
                    <div class="button dpad-btn" id="btn-up" style="grid-column: 2 / 3; grid-row: 1 / 2;">UP</div>
                    <div class="button dpad-btn" id="btn-left" style="grid-column: 1 / 2; grid-row: 2 / 3;">LEFT</div>
                    <div class="dpad-center" style="grid-column: 2 / 3; grid-row: 2 / 3;"></div>
                    <div class="button dpad-btn" id="btn-right" style="grid-column: 3 / 4; grid-row: 2 / 3;">RIGHT</div>
                    <div class="button dpad-btn" id="btn-down" style="grid-column: 2 / 3; grid-row: 3 / 4;">DOWN</div>
                </div>

                <!-- PS Button -->
                <div class="button" id="btn-ps">PS</div>
            </div>
          </div>

          <script>
            let interval = null;
            let busy = false;
            
            // Map the gamepad button index to the HTML element ID
            const BUTTON_MAP = [
              { index: 0, id: 'btn-cross' }, 
              { index: 1, id: 'btn-circle' }, 
              { index: 2, id: 'btn-square' }, 
              { index: 3, id: 'btn-triangle' }, 
              { index: 4, id: 'btn-L1' },
              { index: 5, id: 'btn-R1' },
              { index: 6, id: 'btn-L2' }, // Digital (also analog value used below)
              { index: 7, id: 'btn-R2' }, // Digital (also analog value used below)
              { index: 8, id: 'btn-share' },
              { index: 9, id: 'btn-options' },
              { index: 10, id: 'btn-L3' },
              { index: 11, id: 'btn-R3' },
              { index: 12, id: 'btn-up' },
              { index: 13, id: 'btn-down' },
              { index: 14, id: 'btn-left' },
              { index: 15, id: 'btn-right' },
              { index: 16, id: 'btn-ps' },
            ];

            function getBitmask(buttons) {
                let mask = 0;
                // Gamepad API buttons 0-16.
                for (let i = 0; i < buttons.length && i < 17; i++) {
                    // Note: L2/R2 can be digital or analog. For the mask, we check .pressed.
                    if (buttons[i].pressed) {
                        mask += (1 << i);
                    }
                }
                return mask;
            }

            function updateGraphics(gp, lx_tx, ly_tx, rx_tx, ry_tx, l2_tx, r2_tx) {
                // 1. Sticks
                // The TX variables are float strings: -1.00 to 1.00
                // We map this to a percentage offset for CSS translate: -50px to 50px (half the container size)
                const ls_x_pos = parseFloat(lx_tx) * 50; // -50 to 50
                const ls_y_pos = parseFloat(ly_tx) * 50; // -50 to 50 (Y is inverted in TX logic)
                document.getElementById("ls-pos").style.transform = `translate(calc(-50% + ${ls_x_pos}px), calc(-50% - ${ls_y_pos}px))`; // Note: Y is inverted in CSS transform to match cartesian logic
                
                const rs_x_pos = parseFloat(rx_tx) * 50;
                const rs_y_pos = parseFloat(ry_tx) * 50;
                document.getElementById("rs-pos").style.transform = `translate(calc(-50% + ${rs_x_pos}px), calc(-50% - ${rs_y_pos}px))`; // Note: Y is inverted in CSS transform to match cartesian logic

                // 2. Triggers
                const l2_height = parseFloat(l2_tx) * 100; // 0 to 100
                const r2_height = parseFloat(r2_tx) * 100;
                document.getElementById("l2-fill").style.height = `${l2_height}%`;
                document.getElementById("r2-fill").style.height = `${r2_height}%`;
                
                // Update text display for trigger values
                document.querySelector('.triggers-container div:first-child').innerText = `L2 Value (${l2_tx})`;
                document.querySelector('.triggers-container div:last-child').innerText = `R2 Value (${r2_tx})`;


                // 3. Buttons
                BUTTON_MAP.forEach(item => {
                    const button = gp.buttons[item.index];
                    const element = document.getElementById(item.id);
                    
                    if (element && button) {
                        if (button.pressed) {
                            element.classList.add('active-btn');
                        } else {
                            element.classList.remove('active-btn');
                        }
                    }
                });
            }

            window.addEventListener("gamepadconnected", (e) => {
              document.getElementById("status").innerText = "Link Active";
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
              if (busy) return;

              // Raw axes/triggers
              const lx = gp.axes[0];
              const ly_raw = gp.axes[1];
              const rx = gp.axes[2];
              const ry_raw = gp.axes[3];
              const l2_val = gp.buttons[6].value; // L2 as analog
              const r2_val = gp.buttons[7].value; // R2 as analog
              const mask = getBitmask(gp.buttons);

              // 1. Invert Y-axis and apply deadzone/rounding for transmission
              const ly = -ly_raw;
              const ry = -ry_raw;

              const lx_tx = Math.abs(lx) < 0.1 ? 0.0 : lx.toFixed(2);
              const ly_tx = Math.abs(ly) < 0.1 ? 0.0 : ly.toFixed(2);
              const rx_tx = Math.abs(rx) < 0.1 ? 0.0 : rx.toFixed(2);
              const ry_tx = Math.abs(ry) < 0.1 ? 0.0 : ry.toFixed(2);
              const l2_tx = l2_val.toFixed(2);
              const r2_tx = r2_val.toFixed(2);
              
              // Update Graphical Debug Interface
              updateGraphics(gp, lx_tx, ly_tx, rx_tx, ry_tx, l2_tx, r2_tx);

              // 2. Send
              busy = true;
              fetch(`/update?ax=${lx_tx},${ly_tx},${rx_tx},${ry_tx}&tr=${l2_tx},${r2_tx}&mk=${mask}`)
                .then(response => {
                    busy = false;
                })
                .catch(e => {
                    busy = false;
                });
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
                    parts = p.split('=')
                    if len(parts) != 2: continue
                    key, val = parts
                    
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
        except: 
            return "ERROR"

    def update(self):
        r, _, _ = select.select([self.socket], [], [], 0)
        if r:
            try:
                cl, _ = self.socket.accept()
                req = cl.recv(1024)
                if self.parse_request(req) == "HOME":
                    cl.send(b'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                    cl.send(self.html.encode('utf-8'))
                else:
                    cl.send(b'HTTP/1.0 200 OK\r\n\r\n')
                cl.close()
            except OSError as e:
                # Catch connection-related errors (e.g., socket timeout, connection reset by peer)
                # print(f"[ERROR] Controller: Socket operation failed: {e}") 
                pass
            except Exception as e:
                # Catch any remaining unexpected errors during request processing
                # print(f"[ERROR] Controller: Unexpected error in update loop: {e}")
                pass