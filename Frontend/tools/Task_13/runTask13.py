import ezdxf
from ezdxf.addons.drawing.matplotlib import qsave
import os
import cv2
import numpy as np

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.global_var import AGENT_API_KEY
from utils.file_classifier import classify_input_files
from utils.decorator import dict_to_chat_html_with_cv2_image

import logging
logging.getLogger("ezdxf.addons.drawing.frontend").setLevel(logging.ERROR)
logging.getLogger("ezdxf.addons.drawing").setLevel(logging.ERROR)
logging.getLogger("ezdxf").setLevel(logging.ERROR)

API_KEY = AGENT_API_KEY

layers_to_check = ['TT-BUUDIEN', 'Tuyen chinh TTLL']
prefix_layer_khungten = 'xref_bdh_khungtena2$0$XREF-KHUNG A2-Songhong$0$'

def detect_duong_day(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def detect_tu_dien(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def TTLL_main(input_dxf_dir: str, process_folder = None, output_folder = None, output_name = "Task_13.png"):
    result = {'Đường dây liên lạc': [], 'Tủ điện': []}
    doc = ezdxf.readfile(input_dxf_dir)
    msp = doc.modelspace()
    
    # Set layers before any rendering
    output_folder += f"/{output_name}"
    process_folder += f"/{output_name}"
    
    for layer in doc.layers:
        if layer.dxf.name.startswith(prefix_layer_khungten) or layer.dxf.name in layers_to_check:
            layer.on()
        else:
            layer.off()
   
    qsave(msp, process_folder, size_inches=(16.5, 11.6), bg="#FFFFFF")
    image = cv2.imread(process_folder)
    if image is None:
        result['Đường dây liên lạc'].append("Không đọc được ảnh từ file DXF")
        result['Tủ điện'].append("Không đọc được ảnh từ file DXF")
        return result
    output_image = image.copy()
    blue_contours = detect_duong_day(image)
    if len(blue_contours) >= 2:
        result['Đường dây liên lạc'].append("Bản vẽ có bố trí đường dây")
    else:
        result['Đường dây liên lạc'].append("Bản vẽ không có bố trí đường dây")
    green_contours = detect_tu_dien(image)
    if len(green_contours) >= 2:
        result['Tủ điện'].append("Bản vẽ có bố trí tủ điện")
    else:
        result['Tủ điện'].append("Bản vẽ không có bố trí tủ điện")
    cv2.drawContours(output_image, blue_contours, -1, (0, 0, 255), 3)
    cv2.drawContours(output_image, green_contours, -1, (0, 255, 255), 3)
    cv2.imwrite(output_folder, output_image)

    result["image"] = image

    return result

def runTask13(session_dir, single = True):
    input_folder = os.path.join(session_dir, "input")
    process_folder = os.path.join(session_dir, "process")
    output_folder = os.path.join(session_dir, "output")
    
    files = classify_input_files(input_folder)
    dxf_files = files.get("task13", [])
    if not dxf_files:
        print("[ERROR] Không tìm thấy file DXF cho task13")
        return "Không tìm thấy file DXF cho task13"
    dxf_file = dxf_files[0]
    try:
        result = TTLL_main(dxf_file, process_folder, output_folder)

    except Exception as e:
        return f"Error: {e}"
    
    if single:
        return dict_to_chat_html_with_cv2_image(result)
    
    return result