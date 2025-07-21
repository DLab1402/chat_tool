import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
OCR_DIR = os.path.abspath(os.path.join(CURRENT_DIR,"..","..",".."))
UPLOAD_DIR = os.path.join(BACKEND_DIR,"Upload_data")
print(os.path.join(OCR_DIR, "OCR","tesseract.exe"))
import pytesseract

pytesseract.pytesseract.tesseract_cmd = os.path.join(OCR_DIR, "OCR","tesseract.exe")

session_folders = {}

# AGENT_API_KEY = "AIzaSyDRX2Ru21b-vy-cFkQZjI4fxPHxOwfPfig"
AGENT_API_KEY = "AIzaSyBLH04Gkgnr_vXvZtuGowwhNedpE_--xxs"

TEMPLATE_PATH = os.path.join(CURRENT_DIR, "Backend","utils","Bảng đối chiếu quy hoạch.docx")

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

MCP_IP = "127.0.0.1"
MCP_PORT = 9000