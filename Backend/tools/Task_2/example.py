from Task2_1 import process_image_pipeline
from Task2_2 import detect_parking_areas
import os
from scale_ratio import convert_dxf_to_png_scale_ratio
import glob

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
#layers_rg_qh = ["BCP_MD_Xref_Ranhdat$0$BV_Rg_lapquyhoach"]
#layer_GTNB = "BCP_MD_Xref_MBTT$0$$0$ARTIUS - DRAW"
layer_GTNB = "xref_bct2_tong the$0$QH_DAT_CTHTKT_DuongGT"

input_folder = os.path.join(os.getcwd(), "input")
output_folder = os.path.join(os.getcwd(), "output")

dxf_files = glob.glob(os.path.join(input_folder, "*.dxf"))
if len(dxf_files) == 0:
    raise FileNotFoundError("Không tìm thấy file DXF nào trong thư mục input.")
else:
    dxf_file = dxf_files[0]  

image_path = os.path.join(output_folder, "origin_task2.png")
binary_path = os.path.join(output_folder, "hatch_task2.png")

ratio = convert_dxf_to_png_scale_ratio(dxf_file, output_folder, layers_rg_qh, layers_to_check, layer_GTNB, dpi=300, bg='#FFFFFF')

process_image_pipeline(image_path, binary_path)

detect_parking_areas(image_path, ratio)


