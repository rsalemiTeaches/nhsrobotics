# Library: Alvik Web Controller
# Hides the complexity of WiFi, Sockets, and HTML parsing.
#
# Usage:
#   ctl = Controller(ssid="Alvik-Student-1")
#   ctl.begin()
#   ctl.update()
#   print(ctl.left_stick_y)

import network
import socket
import select
import time

class Controller:
    def __init__(self, ssid="Alvik-Link", password="password"):
        # Configuration
        self.ssid = ssid
        self.password = password
        
        # State Variables (Accessible by Student)
        self.left_stick_y = 0.0   # -1.0 to 1.0
        self.right_stick_y = 0.0  # -1.0 to 1.0
        self.button_x = False
        self.button_o = False
        self.connected = False
        
        # Internal Networking
        self.ap = network.WLAN(network.AP_IF)
        self.socket = None
        
        # The Webpage that runs on the Chromebook/Phone
        # We inject the SSID into the title so the student knows they are on the right page
        self.html = """
        <!DOCTYPE html>
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body { font-family: sans-serif; background: #222; color: #fff; text-align: center; }
            .box { padding: 20px; background: #444; margin: 20px auto; max-width: 400px; border-radius: 10px; }
            .active { background: #00AA00 !important; }
            h1 { margin-bottom: 5px; }
          </style>
        </head>
        <body>
          <h1>""" + self.ssid + """ Controller</h1>
          <div id="status" class="box">1. Connect Controller via Bluetooth<br>2. Press any button</div>
          <div class="box">Left: <span id="l_val">0</span> | Right: <span id="r_val">0</span></div>

          <script>
            let interval = null;
            
            // Detect Controller
            window.addEventListener("gamepadconnected", (e) => {
              document.getElementById("status").innerText = "Controller Active!";
              document.getElementById("status").classList.add("active");
              // Start sending data 10 times a second (100ms)
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

              // Read Joysticks (Standard Mapping)
              // Axis 1 = Left Stick Y, Axis 3 = Right Stick Y
              // Invert them so Up is Positive
              let ly = -gp.axes[1];
              let ry = -gp.axes[3];
              let btnX = gp.buttons[0].pressed ? 1 : 0; // X Button (A on Xbox)
              let btnO = gp.buttons[1].pressed ? 1 : 0; // Circle Button (B on Xbox)

              // Deadzone
              if (Math.abs(ly) < 0.1) ly = 0;
              if (Math.abs(ry) < 0.1) ry = 0;

              // Update Screen
              document.getElementById("l_val").innerText = ly.toFixed(1);
              document.getElementById("r_val").innerText = ry.toFixed(1);

              // Send to Robot via HTTP GET (Fast & Simple)
              // We use fetch with 'no-cors' to be fast/lazy
              fetch(`/update?ly=${ly.toFixed(2)}&ry=${ry.toFixed(2)}&bx=${btnX}&bo=${btnO}`)
                .catch(e => console.log("Lag..."));
            }
          </script>
        </body>
        </html>
        """

    def begin(self):
        """Starts the WiFi AP and Web Server"""
        print(f"Creating WiFi: {self.ssid} ...")
        self.ap.active(True)
        self.ap.config(essid=self.ssid, password=self.password)
        
        while not self.ap.active():
            time.sleep(0.1)
            
        print(f"WiFi Active! IP: {self.ap.ifconfig()[0]}")
        
        # Setup Non-Blocking Socket
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(addr)
        self.socket.listen(1)
        print("Server listening on Port 80")
        print("Go to http://192.168.4.1 in your browser.")

    def parse_request(self, request):
        """Extracts data from URL: /update?ly=0.5&ry=-0.5&bx=1..."""
        try:
            # We are looking for the path inside "GET /update?..."
            request_str = request.decode('utf-8')
            line = request_str.split('\r\n')[0] # First line only
            
            if "GET / " in line:
                return "HOME"
            
            if "/update?" in line:
                # Poor man's parsing to avoid heavy URL libraries
                # Example: /update?ly=1.00&ry=-0.50&bx=0&bo=1
                params = line.split('?')[1].split(' ')[0]
                pairs = params.split('&')
                for p in pairs:
                    key, val = p.split('=')
                    if key == 'ly': self.left_stick_y = float(val)
                    if key == 'ry': self.right_stick_y = float(val)
                    if key == 'bx': self.button_x = (val == '1')
                    if key == 'bo': self.button_o = (val == '1')
                return "DATA"
                
            return "UNKNOWN"
        except:
            return "ERROR"

    def update(self):
        """Check for new data packets (Call this in your loop!)"""
        # Non-blocking check: Is there data waiting?
        # r = ready to read, w = ready to write, e = errors
        r, w, e = select.select([self.socket], [], [], 0)
        
        if r:
            try:
                cl, addr = self.socket.accept()
                request = cl.recv(1024)
                
                req_type = self.parse_request(request)
                
                # Send Response
                if req_type == "HOME":
                    # Send the HTML Page
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                    cl.send(self.html)
                else:
                    # Fast acknowledgement for data updates
                    cl.send('HTTP/1.0 200 OK\r\n\r\n')
                    
                cl.close()
            except OSError:
                pass
            