import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.file_classifier import classify_input_files
from utils.decorator import dict_to_chat_html_with_cv2_image
from tools.Task_4.chieu_rong_final import main

def runTask4(session_dir, single=True):
    input_folder = os.path.join(session_dir, "input")
    output_folder = os.path.join(session_dir, "output")
    os.makedirs(output_folder, exist_ok=True)
    files = classify_input_files(input_folder)
    dxf_files = files.get("task4", [])
    if not dxf_files:
        return "Không tìm thấy file DXF cho task4"
    dxf_file = dxf_files[0]

    try:
        result = main(dxf_file, output_folder)
    except Exception as e:
        return f"Error: {e}"

    if single:
        if isinstance(result, list):
            result_dict = {"Kết quả": item for i, item in enumerate(result)}
            return dict_to_chat_html_with_cv2_image(result_dict)
        return dict_to_chat_html_with_cv2_image(result)

    return result