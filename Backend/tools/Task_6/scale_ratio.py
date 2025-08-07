import cv2
import numpy as np
import ezdxf
import os
from tools.Task_6.binary import convert_GTNB

# Hàm lấy kích thước contour trong ảnh PNG
def get_contour_size(img_dir: str):
    img = cv2.imread(img_dir)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        raise ValueError("No contours found in the image.")
    x, y, w, h = cv2.boundingRect(contours[0])
    return img, w, h

# Hàm lấy bounding box của LWPOLYLINE
def get_lwpolyline_bounding_box(lwpolyline):
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    vertices = list(lwpolyline.vertices())
    for vertex in vertices:
        x, y = vertex[:2]
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)
    return (min_x, min_y, max_x, max_y)

# Hàm vẽ bounding box vào modelspace
def draw_bounding_box(msp, bbox, layer_name="BBOX", color=1):
    min_x, min_y, max_x, max_y = bbox
    corners = [
        (min_x, min_y),
        (max_x, min_y),
        (max_x, max_y),
        (min_x, max_y),
        (min_x, min_y)
    ]
    bbox_polyline = msp.add_lwpolyline(corners)
    bbox_polyline.dxf.layer = layer_name
    bbox_polyline.dxf.color = color
    return bbox_polyline

# Hàm tính chiều rộng và cao từ bbox
def get_height_width(bbox):
    min_x, min_y, max_x, max_y = bbox
    width = max_x - min_x
    height = max_y - min_y
    return height, width

# Hàm chỉnh lại dimpost nếu có
def fix_dimensions_in_block(doc, block_name):
    block = doc.blocks[block_name]
    for entity in block:
        if entity.dxftype() == 'DIMENSION':
            dim_style = doc.dimstyles.get(entity.dxf.dimstyle)
            if dim_style and hasattr(dim_style.dxf, 'dimpost') and dim_style.dxf.dimpost == 'm':
                dim_style.dxf.dimpost = "<>m"

# Hàm explode tất cả INSERT
def explode_all_inserts(doc):
    msp = doc.modelspace()
    while True:
        inserts = [e for e in msp if e.dxftype() == 'INSERT']
        if not inserts:
            break
        for insert in inserts:
            try:
                fix_dimensions_in_block(doc, insert.dxf.name)
                insert.explode()
            except Exception as e:
                print(f"Error exploding insert {insert.dxf.name}: {e}")

# Hàm lọc đối tượng để render
def filter_entities(entity, target_entity_types, layers_to_extract):
    return entity.dxftype() in target_entity_types and entity.dxf.layer in layers_to_extract

# Hàm chính convert và tính scale ratio
def convert_dxf_to_png_scale_ratio(dxf_file, output, layers_rg_qh, layers_to_extract, layer_GTNB, dpi=300, bg='#FFFFFF'):
    doc = ezdxf.readfile(dxf_file)
    msp = doc.modelspace()
    
    # Explode INSERT trước
    explode_all_inserts(doc)
    
    # Duyệt tìm polyline ở lớp cần tính bbox
    for entity in msp:
        if entity.dxftype() == 'LWPOLYLINE' and entity.dxf.layer in layers_rg_qh:
            bbox = get_lwpolyline_bounding_box(entity)
            draw_bounding_box(msp, bbox)
            height, width = get_height_width(bbox)
            print(f"Real height: {height}, Real width: {width}")
            break
    else:
        raise ValueError("No LWPOLYLINE found in specified layers.")

    # Render sang PNG
    convert_GTNB(layers_to_extract, layer_GTNB, doc, output, binary=True)
    convert_GTNB(layers_to_extract, layer_GTNB, doc, output, binary=False)
    # Đọc lại ảnh để lấy kích thước contour
    output_image_path = os.path.join(output, "origin.png")
    _, width_pixel, height_pixel = get_contour_size(output_image_path)

    # Tính tỉ lệ
    scale_factor = height / float(height_pixel)
    print(f"Scale factor is: {scale_factor}")
    return scale_factor

