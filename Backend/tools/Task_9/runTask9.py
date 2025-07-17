import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.file_classifier import classify_input_files
from utils.decorator import dict_to_chat_html_with_cv2_image
from tools.Task_9.converter import draw_trucuuhoa_distances

def runTask9(session_dir, single=True):
    input_folder = os.path.join(session_dir, "input")
    output_folder = os.path.join(session_dir, "output")
    os.makedirs(output_folder, exist_ok=True)
    
    files = classify_input_files(input_folder)
    dxf_files = files.get("task9", [])
    
    if not dxf_files:
        return "Không tìm thấy file DXF cho task9"
    dxf_file = dxf_files[0]
    
    output_file = os.path.join(output_folder, "Task_9.png")
    try:
        result = draw_trucuuhoa_distances(dxf_file, output_file)
    except Exception as e:
        return f"Error: {e}"

    if isinstance(result, dict) and "error" in result:
        return result["error"]

    if single:
        return dict_to_chat_html_with_cv2_image(result)

    return result