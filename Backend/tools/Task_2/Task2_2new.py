import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

def find_green_external_contours(image_path, ratio, show_result=True):
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_green = np.array([40, 50, 50])
    upper_green = np.array([85, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if show_result:
        result = image.copy()
        cv2.drawContours(result, contours, -1, (0, 0, 255), 2)  

        # Đánh số thứ tự lên từng contour
        for idx, contour in enumerate(contours):
            # Tính trung tâm contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = contour[0][0]  # fallback nếu moment bị zero (vd contour quá bé)

            # Vẽ số thứ tự
            cv2.putText(result, str(idx+1), (cx-10, cy+10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)

        # Hiển thị và lưu ảnh
        cv2.imwrite('output/detected_parking_areas.png', result)

    return contours, result

def get_edge_lengths_of_contour(contour, ratio):
    points = contour.reshape(-1, 2)
    edge_lengths = 2**31 - 1 

    num_points = len(points)

    for i in range(num_points):
        pt1 = points[i]
        pt2 = points[(i + 1) % num_points]  # điểm tiếp theo, quay vòng về đầu nếu hết
        length = np.linalg.norm(pt1 - pt2)
        if length < edge_lengths:
            edge_lengths = (length * ratio)
    edge_lengths = np.array(edge_lengths)
    return edge_lengths

def simplify_contour(contour, epsilon_ratio=0.01):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon_ratio * peri, True)
    return approx

def detect(image_path, ratio):
    widths = []
    valid_contours = []
    contours, result = find_green_external_contours(image_path, ratio)
    for idx, contour in enumerate(contours):
        approx = simplify_contour(contour, epsilon_ratio=0.02)
        if len(approx) < 3:
            continue
        edge_lengths = get_edge_lengths_of_contour(approx, ratio)
        if edge_lengths >= 1:
            valid_contours.append(contour)
            widths.append(edge_lengths)
            print(f"    Chiều rộng bãi đỗ là: {np.round(edge_lengths, 2)}m")
        
    print("Tổng số bãi đỗ xe chữa cháy:", len(widths))
    return len(widths), widths, result