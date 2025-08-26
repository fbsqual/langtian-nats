import socket
import json
import time

ADDR = ('127.0.0.1', 9999)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for i in range(10):
    msg = json.dumps({"device_id": f"dev{i}", "voltage": 3.7, "current": 0.5, "timestamp": int(time.time())})
    s.sendto(msg.encode('utf-8'), ADDR)
    time.sleep(0.2)