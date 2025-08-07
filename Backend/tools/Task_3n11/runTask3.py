import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.file_classifier import classify_input_files
from utils.gemini_deco import gemini_to_chatbot_html
from tools.Task_3n11.thuyet_minh_agent import answer_pdf_tai_trong

def runTask3(session_dir):
    input_folder = os.path.join(session_dir, "input")
    files = classify_input_files(input_folder)
    pdf_files = files.get("task3", [])
    if not pdf_files:
        return "Không tìm thấy file PDF cho task3"
    pdf_file = pdf_files[0]
    with open(pdf_file, "rb") as f:
        pdf_bytes = f.read()
    result_text = answer_pdf_tai_trong(pdf_bytes)
    print(result_text)

    return result_text