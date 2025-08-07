import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURRENT_DIR)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
print(BACKEND_DIR)
OCR_DIR = os.path.abspath(os.path.join(CURRENT_DIR,".."))
print(OCR_DIR)

UPLOAD_DIR = os.path.join(BACKEND_DIR, "Backend","Upload_data")
print(UPLOAD_DIR)