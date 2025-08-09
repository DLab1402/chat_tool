import os
import glob
import numpy as np
from main import detect_slope

layers_to_check = [
    "xref_bct2_tong the$0$QH_DAT_CTHTKT_DuongGT",
    "xref_bct2_tong the$0$QHDH_DAT_CTHTKT_DuongGT_CH",
    "xref_bct2_tong the$0$00-HACTH",
    "Text_GT",
] 

input_folder = os.path.join(os.getcwd(), "input")
output_folder = os.path.join(os.getcwd(), "output")

dxf_files = glob.glob(os.path.join(input_folder, "*.dxf"))
if len(dxf_files) == 0:
    raise FileNotFoundError("Không tìm thấy file DXF nào trong thư mục input.")
else:
    dxf_file = dxf_files[0]  

output_image_path = os.path.join(output_folder, "output_slope.png")

block_pairs, count, angle_degs = detect_slope(dxf_file, layers_to_check, output_image_path)

print (f"Tổng số đoạn dốc xác định được: {count}")
for idx, angle_deg in enumerate(angle_degs):
    print(f"Độ dốc {idx + 1}: {angle_deg} độ")