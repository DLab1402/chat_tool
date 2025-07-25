from binary import convert_GTNB
import ezdxf

layers_to_check = [
    # "BTN_MD_Xref_TongThe$0$QH_DAT_Cayxanhhanche",
    # "BTN_MD_Xref_TongThe$0$DAT_NO_Nhaochungcu_BLOCK",
    # "BTN_MD_Xref_TongThe$0$1_Fine line",
    # "BTN_MD_Xref_TongThe$0$DAT_CTHTKT_DuongGTNB",
    # "HT_CN_Cấp nước sạch",
    # "$0$AAP-Dat cay xanh DVO",
    # "$0$ARTIUS - DRAW",
    # "$0$QHDH_DAT_CTHTKT_DuongGT_CH",
    # "A-GENM",
    # "BCP_MD_Xref_MBTT$0$$0$ARTIUS - DRAW",
    # "BCP_MD_Xref_MBTT$0$$0$QHDH_DAT_CTHTKT_DuongGT_CH",
    # "San",
    # "xf_btt_tongthe$0$QH_DAT_CTHTKT_DuongGT",
    # "xf_btt_tongthe$0$QHDH_DAT_CTHTKT_DuongGT_CH",
    # "trucuuhoa",
    "xref_bct2_tong the$0$QH_DAT_CTHTKT_DuongGT",
    "xref_bct2_tong the$0$QHDH_DAT_CTHTKT_DuongGT_CH",
    "BBOX",
] 

layer_GTNB = "xref_bct2_tong the$0$QH_DAT_CTHTKT_DuongGT"

output_folder = r"C:\a_none_unet\Task6_Final\output"

dxf_path = r"C:\a_none_unet\Task6_Final\input\QH03-BV HE THONG GIAO THONG.dxf"
doc = ezdxf.readfile(dxf_path)

convert_GTNB(layers_to_check, layer_GTNB, doc, output_folder, binary=True)
convert_GTNB(layers_to_check, layer_GTNB, doc, output_folder, binary=False)