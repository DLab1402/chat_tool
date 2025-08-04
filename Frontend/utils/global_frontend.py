import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..",".."))
UPLOAD_DIR = os.path.join(ROOT_DIR,"Backend","Upload_data")

STATIC_DIR = os.path.join(FRONTEND_DIR,"static")
TEMP_DIR = os.path.join(FRONTEND_DIR,"templates")

#Data expire setup
# REDIS = redis.from_url("redis://127.0.0.1:6379", decode_responses = True)
REDIS = None
EXPIRE_TIME = 86400 #one day

#Port declear
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