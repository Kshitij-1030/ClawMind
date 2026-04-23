import asyncio
import urllib.request

PI_IP = "192.168.2.3"
PI_PORT = 8888  
COMMAND_FILE = "/tmp/claw_command.txt"

last_cmd = None

async def main():
    print("Direct sender started — sending to Pi at", PI_IP)
    global last_cmd
    while True:
        try:
            with open(COMMAND_FILE, "r") as f:
                cmd = f.read().strip()
            if cmd and cmd != last_cmd:
                try:
                    req = urllib.request.Request(
                        f"http://{PI_IP}:{PI_PORT}/",
                        data=cmd.encode(),
                        method="POST"
                    )
                    urllib.request.urlopen(req, timeout=1)
                    print(f"Sent: {cmd}")
                    last_cmd = cmd
                except Exception as e:
                    print(f"Send error: {e}")
        except FileNotFoundError:
            pass
        await asyncio.sleep(0.05)

asyncio.run(main())