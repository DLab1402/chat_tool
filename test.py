import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
OCR_DIR = BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..",".."))
print(OCR_DIR)