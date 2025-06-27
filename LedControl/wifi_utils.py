import network
import struct
import socket
import machine
import utime
import time
from config_manager import CONFIG_MANAGER

def unquote(string):
    """MicroPython-compatible URL unquote function"""
    import binascii
    parts = string.split('%')
    result = [parts[0]]
    for item in parts[1:]:
        try:
            result.append(binascii.unhexlify(item[:2]).decode('latin-1') + item[2:])
        except:
            result.append('%' + item)
    return ''.join(result)

class WIFI_UTILS:
    def __init__(self, config_manager):
        self.AP_SSID = "Contrib Calendar"
        self.AP_PASSWORD = "setup123"
        self.config_manager = config_manager
        self.NTP_DELTA = 2208988800
        self.host = "pool.ntp.org"
        self.wlan = None
        self.connect_wifi()

    def connect_wifi(self):
        config = self.config_manager.load_config()
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        if "WIFI_SSID" in config and "WIFI_PASSWORD" in config:
            print(f"Connecting to {config['WIFI_SSID']}...")
            self.wlan.connect(config['WIFI_SSID'], config['WIFI_PASSWORD'])
            
            max_attempts = 20
            for _ in range(max_attempts):
                if self.wlan.isconnected():
                    break
                utime.sleep(0.5)
        
        if not self.wlan.isconnected():
            print("Wi-Fi failed. Starting config portal...")
            #self.start_config_portal()
            return
        
        print("Connected! IP:", self.wlan.ifconfig()[0])
        
        self.test_dns()
        self.test_internet()
        self.set_time()

    def start_config_portal(self):
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=self.AP_SSID, password=self.AP_PASSWORD)
        print(f"AP mode active. Connect to '{self.AP_SSID}' and visit http://192.168.4.1")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', 80))
        s.listen(1)
        
        while True:
            conn = None
            try:
                conn, addr = s.accept()
                print('Connection from', addr)
                
                # Receive full request
                request = b''
                while True:
                    chunk = conn.recv(256)
                    if not chunk:
                        break
                    request += chunk
                    if b'\r\n\r\n' in request:  # End of headers
                        break
                
                request = request.decode('utf-8')
                
                if "POST /" in request:
                    # Extract content length
                    content_length = 0
                    for line in request.split('\r\n'):
                        if line.startswith('Content-Length:'):
                            content_length = int(line.split(':')[1].strip())
                            break
                    
                    # Read remaining body if needed
                    body_start = request.find('\r\n\r\n') + 4
                    body = request[body_start:]
                    while len(body) < content_length:
                        body += conn.recv(256).decode('utf-8')
                    
                    # Parse form data
                    config = {}
                    try:
                        for pair in body.split('&'):
                            if '=' in pair:
                                key, value = pair.split('=', 1)
                                config[key] = unquote(value).replace('+', ' ')
                        
                        # Validate required fields
                        required = ['WIFI_SSID', 'WIFI_PASSWORD', 'GITHUB_USERNAME', 
                                  'GITHUB_TOKEN', 'STARTUP_ANIMATION']
                        if all(field in config for field in required):
                            self.config_manager.save_config(config)
                            response = """HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<html>
<body>
<h1>Settings Saved!</h1>
<p>Device will reboot shortly...</p>
</body>
</html>"""
                            conn.send(response.replace('\n', '\r\n'))
                            conn.close()
                            utime.sleep(3)
                            machine.reset()
                        else:
                            raise ValueError("Missing required fields")
                            
                    except Exception as e:
                        print("Error processing form:", e)
                        error_response = """HTTP/1.1 400 Bad Request
Content-Type: text/html
Connection: close

<html>
<body>
<h1>Error</h1>
<p>Please fill all fields.</p>
</body>
</html>"""
                        conn.send(error_response.replace('\n', '\r\n'))
                
                else:
                    # Serve HTML form
                    current_config = self.config_manager.load_config()
                    html = """HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<html>
<body>
<h1>Pico W Configuration</h1>
<form method="POST">
<h2>WiFi Settings</h2>
SSID: <input type="text" name="WIFI_SSID" value="{WIFI_SSID}" required><br>
Password: <input type="password" name="WIFI_PASSWORD" value="{WIFI_PASSWORD}" required><br>

<h2>GitHub Settings</h2>
Username: <input type="text" name="GITHUB_USERNAME" value="{GITHUB_USERNAME}" required><br>
Token: <input type="password" name="GITHUB_TOKEN" value="{GITHUB_TOKEN}" required><br>
<small>(Create token at github.com/settings/tokens)</small><br>

<h2>Calendar Settings</h2>
Startup Animation: <input type="text" name="STARTUP_ANIMATION" value="{STARTUP_ANIMATION}" required><br>
<small>(0: None, 1: Sequential pop, 2: Color wave, 3: Sparkle)</small><br>

<button type="submit">Save Settings</button>
</form>
</body>
</html>""".format(
                        WIFI_SSID=current_config.get('WIFI_SSID', ''),
                        WIFI_PASSWORD=current_config.get('WIFI_PASSWORD', ''),
                        GITHUB_USERNAME=current_config.get('GITHUB_USERNAME', ''),
                        GITHUB_TOKEN=current_config.get('GITHUB_TOKEN', ''),
                        STARTUP_ANIMATION=current_config.get('STARTUP_ANIMATION', '')
                    )
                    conn.send(html.replace('\n', '\r\n'))
                    
            except Exception as e:
                print("Server error:", e)
            finally:
                if conn:
                    conn.close()
     
    def set_time(self):
        """Sync RTC with NTP and set local New York time (auto-adjusts for DST)."""
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        try:
            addr = socket.getaddrinfo(self.host, 123)[0][-1]
        except Exception as e:
            print("DNS resolution failed for NTP server:", e)
            return
            
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(1)
            s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
        except Exception as e:
            print("NTP sync failed:", e)
            return
        finally:
            s.close()
        
        val = struct.unpack("!I", msg[40:44])[0]
        t = val - self.NTP_DELTA  # Get UTC timestamp
        
        # Check if daylight saving time is active (New York rules)
        tm_utc = time.gmtime(t)
        year = tm_utc[0]
        # DST starts 2nd Sunday March, ends 1st Sunday November
        dst_start = time.mktime((year, 3, 8 - (time.mktime((year, 3, 1, 0, 0, 0, 0, 0)) // 86400) % 7, 2, 0, 0, 0, 0))
        dst_end = time.mktime((year, 11, 1 - (time.mktime((year, 11, 1, 0, 0, 0, 0, 0)) // 86400) % 7, 2, 0, 0, 0, 0))
        is_dst = dst_start <= t < dst_end
        
        timezone_offset = -4 if is_dst else -5  # EDT (UTC-4) or EST (UTC-5)
        t_local = t + (timezone_offset * 3600)  # Adjust for local time
        
        tm_local = time.gmtime(t_local)
        machine.RTC().datetime((tm_local[0], tm_local[1], tm_local[2], tm_local[6] + 1, 
                              tm_local[3], tm_local[4], tm_local[5], 0))
        print("New York time synced:", tm_local)
        
    def test_dns(self):
        try:
            addr = socket.getaddrinfo("google.com", 80)[0][-1]
            print("✅ DNS works! IP:", addr[0])
        except Exception as e:
            print("❌ DNS failed:", e)
            
    def test_internet(self):
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect(("142.250.190.46", 80))  # Google IP
            s.close()
            print("✅ Internet works!")
        except Exception as e:
            print("❌ No internet:", e)
