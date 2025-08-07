from scale_ratio import convert_dxf_to_png_scale_ratio
import os
import glob
import torch
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
from skimage.morphology import skeletonize
from ultralytics import YOLO
from shapely.geometry import LineString, Polygon

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
#layers_rg_qh = ['xref_bct2_tong the$0$210129_BConsAnbinh$0$QH_Ranh giới lập quy hoạch']
#layers_rg_qh = ["BTN_MD_Xref_TongThe$0$BV_Rg_lapquyhoach"]
layers_rg_qh = ["BCP_MD_Xref_Ranhdat$0$BV_Rg_lapquyhoach"]

#layer_GTNB = "xref_bct2_tong the$0$QH_DAT_CTHTKT_DuongGT"
layer_GTNB = "BCP_MD_Xref_MBTT$0$$0$ARTIUS - DRAW"

input_folder = os.path.join(os.getcwd(), "input")
output_folder = os.path.join(os.getcwd(), "output")

dxf_files = glob.glob(os.path.join(input_folder, "*.dxf"))
if len(dxf_files) == 0:
    raise FileNotFoundError("Không tìm thấy file DXF nào trong thư mục input.")
else:
    dxf_file = dxf_files[0]  

origin_path = os.path.join(output_folder, "origin.png")
binary_path = os.path.join(output_folder, "hatch.png")

ratio = convert_dxf_to_png_scale_ratio(dxf_file, output_folder, layers_rg_qh, layers_to_check, layer_GTNB, dpi=300, bg='#FFFFFF')
pixel_length, pixel_width = 100/ ratio, 7/ ratio

def process_drawing(origin_path, binary_path, avoid_model_path, dpi=300,
                    image_height=1200, image_width=1200, display_result=True):

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ================= Load model
    avoid_model = YOLO(avoid_model_path)

    # ================= Load and resize image
    image = np.array(Image.open(origin_path).convert("RGB"))
    binary = np.array(Image.open(binary_path).convert("RGB"))
    binary = cv2.cvtColor(binary, cv2.COLOR_RGB2GRAY)
    image = cv2.resize(image, (image_width, image_height))
    binary = cv2.resize(binary, (image_width, image_height))
    # ================= Predict mask
    test_transform = A.Compose([
        A.Resize(height=image_height, width=image_width),
        A.Normalize(mean=[0, 0, 0], std=[1, 1, 1], max_pixel_value=255.0),
        ToTensorV2()
    ])
    augmented, augmented_binary = test_transform(image=image), test_transform(image=binary)
    input_image = augmented['image'].unsqueeze(0).to(device)
    input_binary = augmented_binary['image'].unsqueeze(0).to(device)

    pred_mask_np = input_binary.to(device).squeeze().numpy()
    mask_binary = (pred_mask_np * 255).astype(np.uint8)
    mask_binary = (mask_binary > 200).astype(np.uint8) * 255
    mask_binary = 255 - mask_binary

    # ================= Find largest connected component
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_binary)
    largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    largest_mask = (labels == largest_label).astype(np.uint8) * 255
    
    # ================= Skeletonize and approximate contours
    bool_mask = largest_mask > 0
    skeleton = skeletonize(bool_mask).astype(np.uint8) * 255

    contours, _ = cv2.findContours(skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    epsilon_ratio = 0.003
    approx_contours = []
    for cnt in contours:
        epsilon = epsilon_ratio * cv2.arcLength(cnt, closed=False)
        approx = cv2.approxPolyDP(cnt, epsilon, closed=False)
        approx_contours.append(approx)

    contour_img = np.zeros_like(skeleton)
    cv2.drawContours(contour_img, approx_contours, -1, 255, 1)

    # ================= Detect line segments
    lines = cv2.HoughLinesP(contour_img, 1, np.pi/180, threshold=20, minLineLength=20, maxLineGap=10)
    if lines is None:
        print("Không phát hiện đoạn thẳng nào.")
        return

    # ================= Tính chiều dài, chiều rộng từng đoạn
    all_segments_info = []
    h, w = largest_mask.shape
    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.hypot(x2 - x1, y2 - y1)
        if length < 1/ratio:
            continue

        mx, my = int((x1 + x2) / 2), int((y1 + y2) / 2)
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            continue
        perp_dx, perp_dy = -dy, dx
        perp_len = np.hypot(perp_dx, perp_dy)
        perp_dx /= perp_len
        perp_dy /= perp_len

        dist_pos, dist_neg, step_size = 0, 0, 1
        cx, cy = mx, my
        while 0 <= int(cx) < w and 0 <= int(cy) < h and largest_mask[int(cy), int(cx)] > 0:
            cx += perp_dx * step_size
            cy += perp_dy * step_size
            dist_pos += step_size
        cx, cy = mx, my
        while 0 <= int(cx) < w and 0 <= int(cy) < h and largest_mask[int(cy), int(cx)] > 0:
            cx -= perp_dx * step_size
            cy -= perp_dy * step_size
            dist_neg += step_size
        total_width = dist_pos + dist_neg
        if total_width < 5:
            continue
        all_segments_info.append(((x1, y1, x2, y2), length, total_width))

    # ================= Detect avoid boxes bằng YOLOv8
    avoid_results = avoid_model(image, save=False)
    obb_result = avoid_results[0].obb
    avoid_boxes = []
    if obb_result is not None:
        for obb in obb_result.xyxyxyxy:
            obb_pts = obb.cpu().numpy().reshape(4, 2)
            avoid_boxes.append(obb_pts)

    def check_intersect_shapely(line, obb_boxes):
        x1, y1, x2, y2 = line
        line_geom = LineString([(x1, y1), (x2, y2)])
        for pts in obb_boxes:
            polygon = Polygon(pts)
            if line_geom.intersects(polygon):
                return True
        return False

    final_segments = []
    for info in all_segments_info:
        (x1, y1, x2, y2), length, width = info
        if width < pixel_width and length > pixel_length:
            if not check_intersect_shapely((x1, y1, x2, y2), avoid_boxes):
                final_segments.append(((x1, y1, x2, y2), length, width))

    # ================= Vẽ kết quả
    output_img = image.copy()
    for (x1, y1, x2, y2), length, width in final_segments:
        cv2.line(output_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(output_img, f"{length:.1f},{width:.1f}", (x1, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # Vẽ avoid boxes
    valid_boxes, invalid_boxes = [], []
    for idx, obb_pts in enumerate(avoid_boxes):
        p0, p1, p2, p3 = obb_pts
        edge1 = np.linalg.norm(p0 - p1)
        edge2 = np.linalg.norm(p1 - p2)
        length = max(edge1, edge2)
        width = min(edge1, edge2)
        box_info = {"id": idx+1, "pts": obb_pts, "length": length, "width": width}
        if length > 8/ratio and width > 7/ratio:
            valid_boxes.append(box_info)
        else:
            invalid_boxes.append(box_info)

    for box in valid_boxes:
        pts = np.array(box["pts"], dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(output_img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        x, y = int(pts[0][0][0]), int(pts[0][0][1])
        text = f"{box['id']}|{box['length']:.1f},{box['width']:.1f}"
        cv2.putText(output_img, text, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    for box in invalid_boxes:
        pts = np.array(box["pts"], dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(output_img, [pts], isClosed=True, color=(0, 255, 255), thickness=2)
        x, y = int(pts[0][0][0]), int(pts[0][0][1])
        text = f"{box['id']}|{box['length']:.1f},{box['width']:.1f}"
        cv2.putText(output_img, text, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

    if display_result:
        plt.figure(figsize=(10, 10))
        plt.imshow(cv2.cvtColor(output_img, cv2.COLOR_BGR2RGB))
        plt.title("Final Output")
        plt.axis("off")
        plt.show()

    return final_segments, valid_boxes, invalid_boxes, output_img

final_segments, valid_boxes, invalid_boxes, result_img = process_drawing(
    origin_path, binary_path,
    avoid_model_path="./weights_dtx_detections.pt",
    dpi=300
)

#In ra danh sách đường và bounding box
if not final_segments:
    print("Không có đoạn nội bộ nào cần kiểm tra")
else:
    print("Các đoạn nội bộ cần kiểm tra:")
    for idx, ((x1, y1, x2, y2), length, width) in enumerate(final_segments):
        print(f"Đoạn {idx+1}: ({x1},{y1})-({x2},{y2}) | Chiều dài: {(length*ratio):.1f}m | Chiều rộng: {(width*ratio):.1f}m")
if not valid_boxes and not invalid_boxes:
    print("Không có đoạn tránh xe nào được phát hiện")
else:
    if valid_boxes:
        for box in valid_boxes:  
            print(f"Đoạn tránh xe hợp lệ {box['id']} | Chiều dài: {(box['length']*ratio):.1f} | Chiều rộng: {(box['width']*ratio*0.8029):.1f}")
    else:
        print("Không có đoạn tránh xe hợp lệ nào")
    if invalid_boxes:
        for box in invalid_boxes:
            print(f"Đoạn tránh xe không hợp lệ {box['id']} | Chiều dài: {(box['length']*ratio):.1f} | Chiều rộng: {(box['width']*ratio*0.8029):.1f}")
    else:
        print("Không có đoạn tránh xe không hợp lệ nào")