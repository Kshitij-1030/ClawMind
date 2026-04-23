import serial
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

arduino = None
last_command = None

def connect_arduino():
    global arduino
    ports = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyUSB0', '/dev/ttyUSB1']
    for port in ports:
        try:
            arduino = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)
            print(f"Arduino connected on {port}")
            return True
        except:
            continue
    print("Arduino not found — running without serial")
    return False

def send_to_arduino(cmd):
    global last_command
    if arduino and cmd != last_command:
        try:
            arduino.write((cmd + '\n').encode())
            last_command = cmd
            print(f"Sent to Arduino: {cmd}")
        except Exception as e:
            print(f"Serial error: {e}")

class CommandHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        cmd = self.rfile.read(length).decode().strip()
        send_to_arduino(cmd)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass

connect_arduino()
print("Bridge HTTP server running on port 8888...")
server = HTTPServer(('0.0.0.0', 8888), CommandHandler)
server.serve_forever()