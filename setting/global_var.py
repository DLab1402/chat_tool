import os
import json
import pytesseract

#Current session folders
session_folders = {}

#Path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..",".."))
APP_DIR = os.path.abspath(os.path.join(ROOT_DIR, "bcons", "app"))
MCP_DIR = os.path.abspath(os.path.join(ROOT_DIR, "bcons", "mcp")) 
UPLOAD_DIR = os.path.join(ROOT_DIR,"bcons","Upload_data")

STATIC_DIR = os.path.join(APP_DIR,"static")
TEMP_DIR = os.path.join(APP_DIR,"templates")
TEMPLATE_PATH = os.path.join(CURRENT_DIR, "Bảng đối chiếu quy hoạch.docx")
pytesseract.pytesseract.tesseract_cmd = os.path.join(ROOT_DIR, "OCR","tesseract.exe")

#Load setting
with open(os.path.join(CURRENT_DIR, "setting.json"), "r") as file:
    # 2. Load its content into a Python object
    para = json.load(file)

#IPs and Ports
APP_IP = para["para"]["app_ip"]
APP_PORT = para["para"]["app_port"]

MCP_IP = para["para"]["mcp_ip"]
MCP_PORT = para["para"]["mcp_port"]

APP_URL = f"http://{APP_IP}:{str(APP_PORT)}"
MCP_URL = f"http://{MCP_IP}:{str(MCP_PORT)}"

# API Key and Model
AGENT_API_KEY = para["para"]["key"]
GEMINI_MODEL = para["para"]["model"]

#Layers
layers_rg_qh=para["layers"]["layers_rg_qh"]
#layers task 1n12
layers_to_extract_task1=para["layers"]["layers_to_extract_task1"]
layers_block_task1=para["layers"]["layers_block_task1"]
layers_TTLL_task13 = para["layers"]["layers_TTLL_task13"]
layers_to_draw_task13=para["layers"]["layers_to_draw_task13"]
#layers task 4
layer_dat_nha_o_task4=para["layers"]["layer_dat_nha_o_task4"]
layer_to_extract_task4=para["layers"]["layer_to_extract_task4"]
#layers task 2
layers_to_check_2 = para["layers"]["layers_to_check_2"]
layers_rg_qh_2 = para["layers"]["layers_rg_qh_2"]
layer_GTNB_2 = para["layers"]["layer_GTNB_2"]
#layers task 5
layers_to_check_5 = para["layers"]["layers_to_check_5"]
#layers task 6
layers_to_check_6 = para["layers"]["layers_to_check_6"]
layers_rg_qh_6 = para["layers"]["layers_rg_qh_6"]
layer_GTNB_6 = para["layers"]["layer_GTNB_6"]
#layers task 9
layer_cuuhoa = para["layers"]["layer_cuuhoa"]
layer_GTNB_9 = para["layers"]["layer_GTNB_9"]

#User list
USERS = para["users"]

#Expired
EXPIRE_TIME = para["expire"]
TRIGGER_TIME = para["trigger"]