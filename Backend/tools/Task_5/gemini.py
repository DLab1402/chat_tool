# file: extract_slope_values.py
from ultralytics import YOLO
import cv2
import google.generativeai as genai
import base64
import matplotlib.pyplot as plt

# Khởi tạo Gemini model một lần
genai.configure(api_key="AIzaSyC17ObaX5wh2pC1xIR4cSjInZfM7q230NA")
gemini_model = genai.GenerativeModel('gemini-1.5-flash')


def encode_image_cv2(image):
    """Chuyển ảnh OpenCV sang base64 string"""
    _, buffer = cv2.imencode('.png', image)
    return base64.b64encode(buffer).decode()


def analyze_slope_boxes(
    image_path: str,
    yolo_model_path: str,
    padding: int = 100,
    show_crops: bool = False,
    show_all_crops: bool = False
):
    # Load YOLO model và ảnh
    model_yolo = YOLO(yolo_model_path)
    image = cv2.imread(image_path)
    h, w = image.shape[:2]

    # Detect boxes
    results = model_yolo(image)
    boxes = results[0].boxes.xyxy.cpu().numpy()

    output = []

    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        x1_crop = max(0, x1 - padding)
        y1_crop = max(0, y1 - padding)
        x2_crop = min(w, x2 + padding)
        y2_crop = min(h, y2 + padding)
        crop_img = image[y1_crop:y2_crop, x1_crop:x2_crop]

        # Encode ảnh
        encoded_crop = encode_image_cv2(crop_img)

        # Gửi lên Gemini
        response = gemini_model.generate_content(
            contents=[
                {"text": "Trong ảnh này có các giá trị độ cao dạng +xx.xx trong các cặp +xx.xx/+yy.yy nào? Hãy liệt kê các số ở phần tử số, sau đó hãy tính hiệu của chúng"},
                {"inline_data": {"mime_type": "image/png", "data": encoded_crop}}
            ]
        )

        text_result = response.text.strip()
        output.append({
            "box_index": i,
            "box_coords": (x1, y1, x2, y2),
            "text": text_result
        })

        if show_crops:
            cropped_rgb = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
            plt.imshow(cropped_rgb)
            plt.title(f"Cropped Image {i+1}")
            plt.axis('off')
            plt.show()

        print(f"▶️ Text quanh box {i+1}:\n{text_result}\n---------")

    # Hiển thị tất cả crop (nếu bật)
    if show_all_crops and len(boxes) > 0:
        fig, axes = plt.subplots(1, len(boxes), figsize=(5 * len(boxes), 5))
        if len(boxes) == 1:
            axes = [axes]
        for i, (box, ax) in enumerate(zip(boxes, axes)):
            x1, y1, x2, y2 = map(int, box)
            x1_crop = max(0, x1 - padding)
            y1_crop = max(0, y1 - padding)
            x2_crop = min(w, x2 + padding)
            y2_crop = min(h, y2 + padding)
            crop_img = image[y1_crop:y2_crop, x1_crop:x2_crop]
            cropped_rgb = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
            ax.imshow(cropped_rgb)
            ax.set_title(f"Cropped {i+1}")
            ax.axis('off')
        plt.tight_layout()
        plt.show()

    return output
