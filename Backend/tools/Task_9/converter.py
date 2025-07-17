import ezdxf
import math
import matplotlib.pyplot as plt
import os

def draw_trucuuhoa_distances(input_filename, output_filename):
    # Load bản vẽ
    doc = ezdxf.readfile(input_filename)
    msp = doc.modelspace()

    # Lưu tọa độ trụ cứu hỏa
    trucuuhoa_points = []
    for entity in msp:
        if entity.dxf.layer == 'trucuuhoa' and entity.dxftype() == 'INSERT':
            pos = entity.dxf.insert
            trucuuhoa_points.append((pos.x, pos.y))

    print(f"Số lượng trụ cứu hỏa: {len(trucuuhoa_points)}")

    if len(trucuuhoa_points) < 2:
        print(f"Chỉ có {len(trucuuhoa_points)} trụ cứu hỏa, không đủ để tính khoảng cách")
        return {"error": "Không đủ trụ cứu hỏa để tính khoảng cách"}

    # Tính khoảng cách từng cặp
    distances = []
    for i in range(len(trucuuhoa_points)):
        for j in range(i + 1, len(trucuuhoa_points)):
            p1 = trucuuhoa_points[i]
            p2 = trucuuhoa_points[j]
            d = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
            distances.append({"from": p1, "to": p2, "distance": d})
            print(f"Khoảng cách từ {p1} đến {p2}: {d:.2f} m")

    # Tạo figure
    plt.figure(figsize=(12, 12))

    # Vẽ trụ cứu hỏa
    for p in trucuuhoa_points:
        plt.plot(p[0], p[1], 'ro')  # Red circle

    # Vẽ line và ghi khoảng cách
    for item in distances:
        p1, p2, d = item["from"], item["to"], item["distance"]
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'g--', linewidth=1)
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        plt.text(mid_x, mid_y, f"{d:.2f}m", fontsize=8, color='blue')

    # Tùy chỉnh figure
    plt.gca().set_aspect('equal', adjustable='box')
    plt.axis('off')  # Tắt trục tọa độ

    # Lưu hình
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Đã lưu ảnh kết quả tại {output_filename}")
    # Đọc lại ảnh bằng OpenCV để trả về đúng định dạng
    import cv2
    img = cv2.imread(output_filename)
    return {
        "Số lượng trụ cứu hỏa": len(trucuuhoa_points),
        "Khoảng cách giữa các trụ": [f"Từ {item['from']} đến {item['to']}: {item['distance']:.2f} m" for item in distances],
        "image": img
    }
