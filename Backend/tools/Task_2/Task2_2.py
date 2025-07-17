from ultralytics import YOLO
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

def detect_parking_areas(image_path, ratio, show_result=True):
    # Load model từ file cùng thư mục script
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bdx_best.pt')
    model = YOLO(model_path)

    # Đọc ảnh đầu vào
    image = cv2.imread(image_path)
    if image is None:
        print(f"Không đọc được ảnh tại: {image_path}")
        return 0, []

    # Dự đoán segmentation với conf thấp hơn nếu cần
    results = model(image_path, conf=0.1)
    detections = results[0]

    # Kiểm tra xem có mask không
    if detections.masks is None:
        print("Không detect được bãi đỗ xe nào trong ảnh.")
        if show_result:
            cv2.imshow('Detection Result', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return 0, []

    num_parking = 0
    widths = []
    overlay = image.copy()

    for i, seg in enumerate(detections.masks.xy):
        num_parking += 1
        polygon = np.array(seg, dtype=np.int32)

        rect = cv2.minAreaRect(polygon)
        (w, h) = rect[1]
        width = min(w, h) if w > 0 and h > 0 else 0
        widths.append(width)

        cv2.polylines(overlay, [polygon], isClosed=True, color=(0, 255, 0), thickness=2)
        cv2.putText(overlay, f'#{num_parking}', tuple(polygon[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        box = cv2.boxPoints(rect)
        box = np.int32(box)
        cv2.drawContours(overlay, [box], 0, (255, 0, 0), 2)

    print(f'Số bãi đỗ xe detect được: {num_parking}')
    for i, w in enumerate(widths):
        print(f'- Độ rộng của bãi #{i+1}: {(w*ratio):.2f} mét')

    if show_result:
        overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
        
        # plt.figure(figsize=(12, 8))
        # plt.imshow(overlay_rgb)
        # plt.title('Detection Result')
        # plt.axis('off')
        # plt.show()

    return num_parking, widths, overlay_rgb

