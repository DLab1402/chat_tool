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

def runTask2(session_dir, single=True):
    input_folder = os.path.join(session_dir, "input")
    output_folder = os.path.join(session_dir, "output")
    os.makedirs(output_folder, exist_ok=True)
    
    files = classify_input_files(input_folder)
    dxf_files = files.get("task2", [])
    
    if not dxf_files:
        return "Không tìm thấy file DXF cho task2"
    dxf_file = dxf_files[0]

    layers_to_check = [
        "BTN_MD_Xref_TongThe$0$QH_DAT_Cayxanhhanche",
        "BTN_MD_Xref_TongThe$0$DAT_NO_Nhaochungcu_BLOCK",
        "BTN_MD_Xref_TongThe$0$1_Fine line",
        "BTN_MD_Xref_TongThe$0$DAT_CTHTKT_DuongGTNB",
        "HT_CN_Cấp nước sạch",
        "$0$AAP-Dat cay xanh DVO",
        "$0$ARTIUS - DRAW",
        "$0$QHDH_DAT_CTHTKT_DuongGT_CH",
        "A-GENM",
        "BCP_MD_Xref_MBTT$0$$0$ARTIUS - DRAW",
        "BCP_MD_Xref_MBTT$0$$0$QHDH_DAT_CTHTKT_DuongGT_CH",
        "San",
        "xf_btt_tongthe$0$QH_DAT_CTHTKT_DuongGT",
        "xf_btt_tongthe$0$QHDH_DAT_CTHTKT_DuongGT_CH",
        "trucuuhoa",
        "xref_bct2_tong the$0$QH_DAT_CTHTKT_DuongGT",
        "xref_bct2_tong the$0$QHDH_DAT_CTHTKT_DuongGT_CH",
        "BBOX",
    ] 
    layers_rg_qh = ['xref_bct2_tong the$0$210129_BConsAnbinh$0$QH_Ranh giới lập quy hoạch']
    layer_GTNB = "xref_bct2_tong the$0$QH_DAT_CTHTKT_DuongGT"

    image_path = os.path.join(output_folder, "origin_task2.png")
    binary_path = os.path.join(output_folder, "hatch_task2.png")

    ratio = convert_dxf_to_png_scale_ratio(dxf_file, output_folder, layers_rg_qh, layers_to_check, layer_GTNB, dpi=300, bg='#FFFFFF')

    try:
        # Xử lý đường nội bộ
        duong_img, text = process_image_pipeline(image_path, binary_path)
        # Xử lý bãi đỗ xe
        num_parking, widths, bai_do_img = detect(image_path, ratio)
    except Exception as e:
        return f"Error: {e}"

    # Ghép kết quả text giống như terminal
    text_lines = []
    # Đường nội bộ
    if duong_img is not None and text:
        text_lines.append("Các đoạn đường nội bộ:")
        for line in text:
            text_lines.append(f"- {line}")
        # Nếu muốn chi tiết hơn, có thể lấy số đoạn từ log hoặc trả về từ process_image_pipeline
    else:
        text_lines.append("Không phát hiện được đường nội bộ hoặc ảnh lỗi.")

    # Bãi đỗ xe
    if num_parking == 0:
        text_lines.append("Không phát hiện được bãi đỗ xe nào trong ảnh.")
    else:
        text_lines.append(f"Số bãi đỗ xe detect được: {num_parking}")
        for i, w in enumerate(widths):
            text_lines.append(f"- Độ rộng của bãi #{i+1}: {w:.2f} mét")

    # Hiển thị cả hai ảnh nếu có
    result = {"Kết quả": '<br>'.join(text_lines)}
    if duong_img is not None:
        result["Ảnh đường nội bộ"] = duong_img
    if bai_do_img is not None:
        result["Ảnh bãi đỗ xe"] = bai_do_img

    if single:
        return dict_to_chat_html_with_cv2_image(result)
    return result
