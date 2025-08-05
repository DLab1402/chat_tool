from utils.file_classifier import classify_input_files
from utils.decorator import dict_to_chat_html_with_cv2_image
from tools.Task_5.main import detect_slope
import os
import glob
import cv2

def runTask5(session_dir, single = True):

    layers_to_check = [
    "xref_bct2_tong the$0$QH_DAT_CTHTKT_DuongGT",
    "xref_bct2_tong the$0$QHDH_DAT_CTHTKT_DuongGT_CH",
    ] 

    input_folder = os.path.join(session_dir, "input")
    output_folder = os.path.join(session_dir, "output")
    os.makedirs(output_folder, exist_ok=True)

    files = classify_input_files(input_folder)
    dxf_files = files.get("task5", [])
 
    if not dxf_files:
        return "Không tìm thấy file DXF cho task5"
    dxf_file = dxf_files[0]  

    output_image_path = os.path.join(output_folder, "output_slope.png")

    try:
        block_pairs, count, angle_degs = detect_slope(dxf_file, layers_to_check, output_image_path)
    except Exception as e:
        return f"Error: {e}"
    
    if not count:
        result_str_html = "Không tìm thấy đoạn đường dốc nào<br>"
        result_str_text = "Không tìm thấy đoạn đường dốc nào\n"
    else:
        result_str_html = f"Tổng số đoạn dốc xác định được được: {count}<br>"
        result_str_text = f"Tổng số đoạn dốc xác định được được: {count}\n"
        for angle_deg in angle_degs:
            result_str_html += f"Độ dốc: {angle_deg} độ<br>"
            result_str_text += f"Độ dốc: {angle_deg} độ\n"
    if single:
        image = cv2.imread(output_image_path)
        return dict_to_chat_html_with_cv2_image({"Kết quả": result_str_html, "Kết quả phát hiện độ dốc": image})
    
    return result_str_text