import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..",".."))
UPLOAD_DIR = os.path.join(ROOT_DIR,"Backend","Upload_data")

STATIC_DIR = os.path.join(FRONTEND_DIR,"static")
TEMP_DIR = os.path.join(FRONTEND_DIR,"templates")

FORNTEND_IP = "127.0.0.1"
FRONTEND_PORT = 8000

MCP_IP = "127.0.0.1"
MCP_PORT = 9000

AGENT_API_KEY = "AIzaSyBLH04Gkgnr_vXvZtuGowwhNedpE_--xxs"

MCP_SERVER_URL = "http://"+MCP_IP+":"+str(MCP_PORT)
GEMINI_API_KEY = AGENT_API_KEY
GEMINI_MODEL = "models/gemini-1.5-pro-latest"

session_folders = {}