import ezdxf
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms

def detect_slope(dxf_file, layers_to_check, output_image_path):
    # Đọc file DXF
    doc = ezdxf.readfile(dxf_file)
    msp = doc.modelspace()

    blocks = []
    for entity in msp.query('INSERT'):
        if entity.dxf.name == 'CD1':
            pos = entity.dxf.insert
            z_tag1 = None
            for attrib in entity.attribs:
                if attrib.dxf.tag == '1':
                    value_text = attrib.dxf.text.replace('+', '').strip()
                    try:
                        z_tag1 = float(value_text)
                    except ValueError:
                        z_tag1 = None
            if z_tag1 is not None:
                blocks.append({'pos': pos, 'z': z_tag1})

    remaining_blocks = blocks.copy()
    block_pairs = []

    current_block = remaining_blocks.pop(0)

    while remaining_blocks:
        candidate_blocks = [b for b in remaining_blocks if b['z'] != current_block['z']]

        # Nếu không còn block nào khác z thì thoát vòng
        if not candidate_blocks:
            break
        # Tìm block gần nhất trong candidate_blocks
        nearest_block = min(candidate_blocks, key=lambda b: math.hypot(
            b['pos'][0] - current_block['pos'][0],
            b['pos'][1] - current_block['pos'][1]
        ))
        block_pairs.append((current_block, nearest_block))

        # Cập nhật current_block và loại nearest_block khỏi danh sách
        current_block = nearest_block
        remaining_blocks.remove(nearest_block)


    print(f"Tổng số cặp ghép được: {len(block_pairs)}")

    # Tạo figure matplotlib
    fig, ax = plt.subplots(figsize=(12, 12))

    # Vẽ các entity thuộc layer cho phép
    for e in msp:
        layer_name = e.dxf.layer
        if layer_name in layers_to_check:
            if e.dxftype() == 'LINE':
                x_values = [e.dxf.start[0], e.dxf.end[0]]
                y_values = [e.dxf.start[1], e.dxf.end[1]]
                ax.plot(x_values, y_values, 'gray', linewidth=0.5)
            elif e.dxftype() == 'LWPOLYLINE':
                points = e.get_points('xy')
                x_values, y_values = zip(*points)
                ax.plot(x_values, y_values, 'gray', linewidth=0.5)
            elif e.dxftype() == 'INSERT':
                x, y = e.dxf.insert[0], e.dxf.insert[1]
                block = doc.blocks[e.dxf.name]
                for block_entity in block:
                    if block_entity.dxftype() == 'LINE':
                        x_values = [block_entity.dxf.start[0] + x, block_entity.dxf.end[0] + x]
                        y_values = [block_entity.dxf.start[1] + y, block_entity.dxf.end[1] + y]
                        ax.plot(x_values, y_values, 'green', linewidth=1)
    count = 0
    angle_degs = []
    pair_index = 1

    # Sửa đoạn code vẽ hình chữ nhật
    for p1, p2 in block_pairs:
        x1, y1 = p1['pos'][0], p1['pos'][1]
        x2, y2 = p2['pos'][0], p2['pos'][1]
        z1, z2 = p1['z'], p2['z']

        distance = math.hypot(x2 - x1, y2 - y1)
        if distance == 0:
            continue

        # Tính angle theo độ
        angle_deg = round(math.degrees(math.atan((z2 - z1) / distance)), 3)

        if angle_deg > 0:
            count += 1
            angle_degs.append(angle_deg)

            # Midpoint
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2

            # Chiều dài, chiều rộng hình chữ nhật
            rect_length = distance
            rect_width = rect_length * 0.8 

            # Góc xoay của hình chữ nhật
            angle_rad = math.atan2(y2 - y1, x2 - x1)
            angle_deg_text = math.degrees(angle_rad)

            # Vector đơn vị vuông góc (để dịch sang 2 bên)
            dx = x2 - x1
            dy = y2 - y1
            length = math.hypot(dx, dy)
            ux = dx / length  # Vector đơn vị theo hướng đoạn thẳng
            uy = dy / length
            vx = -uy  # Vector vuông góc
            vy = ux

            # Tính tọa độ góc trái dưới của hình chữ nhật
            # Điểm bắt đầu là midpoint dịch chuyển ngược nửa chiều dài và nửa chiều rộng
            start_x = mid_x - (rect_length / 2) * ux - (rect_width / 2) * vx
            start_y = mid_y - (rect_length / 2) * uy - (rect_width / 2) * vy

            # Vẽ rectangle với góc xoay
            rect = patches.Rectangle(
                (start_x, start_y),
                rect_length,
                rect_width,
                angle=angle_deg_text,
                linewidth=1.5,
                edgecolor='red',
                facecolor='none',
                transform=ax.transData
            )
            ax.add_patch(rect)

            # Ghi số thứ tự vào giữa hình chữ nhật
            ax.text(mid_x, mid_y, f"{pair_index}", fontsize=20, rotation=angle_deg_text,
                    ha='center', va='center', color='blue')
            pair_index += 1
    ax.set_aspect('equal')
    ax.axis('off')

    # Lưu hình ảnh
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight')
    plt.close()

    print("Hoàn tất, file output_slope.png đã tạo!")

    return block_pairs, count, angle_degs