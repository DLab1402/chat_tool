import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

STATIC_DIR = os.path.join(FRONTEND_DIR, "Frontend","static")
TEMP_DIR = os.path.join(FRONTEND_DIR, "Frontend","templates")

#Port detect
import socket

def get_ipv4():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to connect — just to get the right interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

FORNTEND_IP = get_ipv4()
FRONTEND_PORT = 8000

BACKEND_IP = "127.0.0.1"
BACKTEND_PORT = 8001