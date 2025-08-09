import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.file_classifier import classify_input_files
from utils.output_collector import output_collector, llm_compare_func_gemini
from tools.Task_3n11.thuyet_minh_agent import answer_pdf_luu_luong

def runTask11(session_dir):
    input_folder = os.path.join(session_dir, "input")
    files = classify_input_files(input_folder)
    pdf_files = files.get("task11", [])
    if not pdf_files:
        return "Không tìm thấy file PDF cho task11"
    pdf_file = pdf_files[0]
    with open(pdf_file, "rb") as f:
        pdf_bytes = f.read()
    result_text = answer_pdf_luu_luong(pdf_bytes)
    return result_text