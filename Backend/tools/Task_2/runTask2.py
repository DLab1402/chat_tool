import os
import sys
import glob
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from utils.file_classifier import classify_input_files
from utils.decorator import dict_to_chat_html_with_cv2_image
from tools.Task_2.Task2_1 import process_image_pipeline
from tools.Task_2.Task2_2 import detect_parking_areas
from tools.Task_2.scale_ratio import convert_dxf_to_png_scale_ratio
from tools.Task_2.Task2_2new import detect 
from utils.global_backend import layers_to_check_2, layers_rg_qh_2, layer_GTNB_2
def runTask2(session_dir, single=True):
    input_folder = os.path.join(session_dir, "input")
    output_folder = os.path.join(session_dir, "output")
    os.makedirs(output_folder, exist_ok=True)

    files = classify_input_files(input_folder)
    dxf_files = files.get("task2", [])

    if not dxf_files:
        return "Không tìm thấy file DXF cho task2"
    dxf_file = dxf_files[0]

    image_path = os.path.join(output_folder, "origin_task2.png")
    binary_path = os.path.join(output_folder, "hatch_task2.png")

    ratio = convert_dxf_to_png_scale_ratio(dxf_file, output_folder, layers_rg_qh_2, layers_to_check_2, layer_GTNB_2, dpi=300, bg='#FFFFFF')

    try:
        # Xử lý đường nội bộ
        duong_img, text = process_image_pipeline(image_path, binary_path)
        # Xử lý bãi đỗ xe
        num_parking, widths, bai_do_img = detect(image_path, ratio)
    except Exception as e:
        return f"Error: {e}"

    # Ghép kết quả text giống như terminal
    text_lines_html = []
    text_lines_word = []
    # Đường nội bộ
    if duong_img is not None and text:
        text_lines_html.append("Các đoạn đường nội bộ:")
        text_lines_word.append("Các đoạn đường nội bộ:")
        for line in text:
            text_lines_html.append(f"- {line}")
            text_lines_word.append(f"- {line}")
    else:
        text_lines_html.append("Không phát hiện được đường nội bộ hoặc ảnh lỗi.")
        text_lines_word.append("Không phát hiện được đường nội bộ hoặc ảnh lỗi.")

    # Bãi đỗ xe
    if num_parking == 0:
        text_lines_html.append("Không phát hiện được bãi đỗ xe nào trong ảnh.")
        text_lines_word.append("Không phát hiện được bãi đỗ xe nào trong ảnh.")
    else:
        text_lines_html.append(f"Số bãi đỗ xe detect được: {num_parking}")
        text_lines_word.append(f"Số bãi đỗ xe detect được: {num_parking}")
        for i, w in enumerate(widths):
            text_lines_html.append(f"- Độ rộng của bãi #{i+1}: {w:.2f} mét")
            text_lines_word.append(f"- Độ rộng của bãi #{i+1}: {w:.2f} mét")

    # Hiển thị cả hai ảnh nếu có
    result_html = {"Kết quả": '<br>'.join(text_lines_html)}
    result_word = {"Kết quả": text_lines_word}  # Trả về danh sách dòng thay vì chuỗi

    if duong_img is not None:
        result_html["Ảnh đường nội bộ"] = duong_img
        result_word["Ảnh đường nội bộ"] = duong_img
    if bai_do_img is not None:
        result_html["Ảnh bãi đỗ xe"] = bai_do_img
        result_word["Ảnh bãi đỗ xe"] = bai_do_img

    if single:
        return dict_to_chat_html_with_cv2_image(result_html)
    return result_word
