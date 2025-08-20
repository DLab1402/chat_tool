import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
OCR_DIR = os.path.abspath(os.path.join(CURRENT_DIR,"..","..",".."))
UPLOAD_DIR = os.path.join(BACKEND_DIR,"Upload_data")

import pytesseract

pytesseract.pytesseract.tesseract_cmd = os.path.join(OCR_DIR, "OCR","tesseract.exe")

session_folders = {}

# AGENT_API_KEY = "AIzaSyDRX2Ru21b-vy-cFkQZjI4fxPHxOwfPfig"
AGENT_API_KEY = "AIzaSyBLH04Gkgnr_vXvZtuGowwhNedpE_--xxs"

TEMPLATE_PATH = os.path.join(CURRENT_DIR, "Bảng đối chiếu quy hoạch.docx")

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

#Expired setup
EXPIRE_TIME = 3600 #one hour
TRIGGER_TIME = 60 #one minute

#Official layers

layers_rg_qh='BV_Rg_lapquyhoach'
#layers task 1n12
layers_to_extract_task1=['QH_KH_BLOCK','BBOX']
layers_block_task1=['DAT_NO_NhaochungCu','QH_NO_ChungCu_Block']
#layers task 13
layers_TTLL_task13 = ['HTKT_CD_Tram', 'HTKT_CD_Tuyen']
layers_to_draw_task13=['DAT_NO_NhaochungCu','DAT_CTHTKT_DuongGT','BV_Rg_lapquyhoach']
#layers task 4
layer_dat_nha_o_task4='DAT_NO_NhaochungCu'
layer_to_extract_task4=['DAT_NO_NhaochungCu','DAT_CTHTKT_DuongGT','BV_Rg_lapquyhoach']
#layers task 2
layers_to_check_2 = ["QH_Xref_TongThe$0$DAT_CTHTKT_DuongGT", "QH_Xref_TongThe$0$ QH_HTKT_HatchGTNB","QH_Xref_TongThe$0$A-GENM", "San", "BBOX"]
layers_rg_qh_2 = ['QH_Xref_TongThe$0$BV_Rg_lapquyhoach']
layer_GTNB_2 = "QH_Xref_TongThe$0$DAT_CTHTKT_DuongGT"
#layers task 5
layers_to_check_5 = [
    "DAT_CTHTKT_DuongGT",
    "QH_HTKT_HatchGTNB",
    "00-HACTH",
    "QH_KH_CaoDoThietKe",
] 
#layers task 6
layers_to_check_6 = [
    "QH_Xref_TongThe$0$DAT_CTHTKT_DuongGT",
    "QH_Xref_TongThe$0$ QH_HTKT_HatchGTNB",
    "BBOX"
] 
layers_rg_qh_6 = ["QH_Xref_TongThe$0$BV_Rg_lapquyhoach"]
layer_GTNB_6 = "QH_Xref_TongThe$0$DAT_CTHTKT_DuongGT"
#layers task 9
layer_cuuhoa = "HTKT_CC_Tuyen"
layer_GTNB_9 = "QH_Xref_TongThe$0$DAT_CTHTKT_DuongGT"