import torch
import numpy as np
import cv2
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2
from shapely.geometry import Polygon, LineString
from skimage.morphology import skeletonize
from ultralytics import YOLO
import matplotlib.pyplot as plt
import os

# ================== Config
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

avoid_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'width_best.pt')
image_width, image_height = 1200, 1200
epsilon_ratio = 0.005

# ================== Load models
avoid_model = YOLO(avoid_model_path)

# ================== Xử lý ảnh input
def preprocess_image(image_path, binary_path, width, height):
    image = np.array(Image.open(image_path).convert("RGB"))
    image_resized = cv2.resize(image, (width, height))
    binary = np.array(Image.open(binary_path).convert("RGB"))
    binary = cv2.cvtColor(binary, cv2.COLOR_RGB2GRAY)
    binary = cv2.resize(binary, (image_width, image_height))
    transform = A.Compose([
        A.Resize(height=height, width=width),
        A.Normalize(mean=[0, 0, 0], std=[1, 1, 1], max_pixel_value=255.0),
        ToTensorV2()
    ])
    tensor_image = transform(image=image_resized)['image'].unsqueeze(0).to(device)
    tensor_binary = transform(image=binary)['image'].unsqueeze(0).to(device)
    pred_mask_np = tensor_binary.to(device).squeeze().numpy()
    mask_binary = (pred_mask_np * 255).astype(np.uint8)
    mask_binary = (mask_binary > 200).astype(np.uint8) * 255
    mask_binary = 255 - mask_binary
    return tensor_image, image_resized, mask_binary

# ================== Skeletonize và lấy contour
def get_skeleton_contours(mask, epsilon_ratio):
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    if num_labels <= 1:
        return [], np.zeros_like(mask)

    largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    largest_mask = (labels == largest_label).astype(np.uint8) * 255

    skeleton = skeletonize(largest_mask > 0).astype(np.uint8) * 255
    contours, _ = cv2.findContours(skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    approx_contours = []
    for cnt in contours:
        epsilon = epsilon_ratio * cv2.arcLength(cnt, False)
        approx = cv2.approxPolyDP(cnt, epsilon, False)
        approx_contours.append(approx)

    return approx_contours, skeleton

# ================== Detect avoid boxes bằng YOLO
def detect_avoid_boxes(model, image):
    results = model(image, save=False, imgsz=1200)
    avoid_boxes = []

    result = results[0]

    # Nếu model có OBB
    if hasattr(result, 'obb') and result.obb is not None and result.obb.xyxyxyxy is not None:
        print(f"Sử dụng OBB, số box: {len(result.obb.xyxyxyxy)}")
        for obb in result.obb.xyxyxyxy:
            pts = obb.cpu().numpy().reshape(4, 2)
            avoid_boxes.append(pts)
    elif result.boxes is not None and result.boxes.xyxy is not None:
        print(f"Sử dụng AABB, số box: {len(result.boxes.xyxy)}")
        for box in result.boxes.xyxy:
            x1, y1, x2, y2 = box.cpu().numpy()
            pts = np.array([[x1, y1],
                            [x2, y1],
                            [x2, y2],
                            [x1, y2]], dtype=np.float32)
            avoid_boxes.append(pts)
    else:
        print("Không có đoạn đường nào có kí hiệu độ rộng!")

    return avoid_boxes

# ================== Lấy tất cả đoạn thẳng từ contour
def get_all_segments(approx_contours):
    segments = []
    for approx in approx_contours:
        for i in range(len(approx) - 1):
            x1, y1 = approx[i][0]
            x2, y2 = approx[i + 1][0]
            segments.append((x1, y1, x2, y2))
    return segments

# ================== Check đoạn thẳng có cắt avoid box không
def check_intersect(line, boxes):
    x1, y1, x2, y2 = line
    line_geom = LineString([(x1, y1), (x2, y2)])
    return any(line_geom.intersects(Polygon(box)) for box in boxes)

# ================== Phân loại đoạn thẳng theo avoid box
def classify_segments(segments, avoid_boxes):
    with_label, without_label = [], []
    for seg in segments:
        if check_intersect(seg, avoid_boxes):
            with_label.append(seg)
        else:
            without_label.append(seg)
    return with_label, without_label

# ================== Vẽ kết quả lên ảnh
def draw_segments_and_boxes(image, with_label, without_label, avoid_boxes):
    for idx, pts in enumerate(avoid_boxes):
        pts_int = np.array(pts, np.int32)
        cv2.polylines(image, [pts_int], True, (0, 255, 255), 2)
        cX, cY = np.mean(pts_int[:, 0]), np.mean(pts_int[:, 1])
        cv2.circle(image, (int(cX), int(cY)), 5, (255, 0, 0), -1)
        cv2.putText(image, str(idx + 1), (int(cX) - 10, int(cY) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    for x1, y1, x2, y2 in with_label:
        cv2.line(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

    for x1, y1, x2, y2 in without_label:
        cv2.line(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

    return image

# ================== Pipeline chính
Text = []
def process_image_pipeline(image_path, binary_path):
    input_tensor, raw_image, mask_binary = preprocess_image(image_path, binary_path, image_width, image_height)
    approx_contours, skeleton = get_skeleton_contours(mask_binary, epsilon_ratio)
    if not approx_contours:
        Text.append("Không tìm thấy đường nội bộ nào!")
        return

    avoid_boxes = detect_avoid_boxes(avoid_model, raw_image)
    Text.append(f"Số kí hiệu độ rộng xác định được: {len(avoid_boxes)}")

    segments = get_all_segments(approx_contours)
    with_label, without_label = classify_segments(segments, avoid_boxes)

    result_image = draw_segments_and_boxes(raw_image.copy(), with_label, without_label, avoid_boxes)

    Text.append(f"Đoạn có độ rộng: {len(with_label)}")
    Text.append(f"Đoạn không có độ rộng: {len(without_label)}")

    return result_image, Text
    # Hiển thị bằng plt
    # plt.figure(figsize=(12, 12))
    # plt.imshow(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
    # plt.title("Kết quả")
    # plt.axis("off")
    # plt.show()

