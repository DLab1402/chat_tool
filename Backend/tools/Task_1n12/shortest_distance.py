import cv2
import numpy as np
import os
import pytesseract
from pytesseract import Output
import ezdxf
from ezdxf.addons.drawing import matplotlib

target_entity_types=['TEXT','MTEXT','LINE', 'POLYLINE', 'LWPOLYLINE']
layers_to_extract=['TAD - TEXT',
                    'BBOX',
                    # 'BTN_MD_Xref_TongThe$0$QH_DAT_NO_Nhaochungcu'
                    # 'xref_bct2_tong the$0$QH_DAT_NO_Nhaochungcu', # do_an 2
                    # 'xref_bct2_tong the$0$2_Visible line'
                    # 'BCP_MD_Xref_MBTT$0$$0$QH_DAT_NO_Nhaochungcu' #do an 5
                    ]
layers_block=['QH_DAT_NO_Nhaochungcu']
layers_rg_qh=['BV_Rg_lapquyhoach',
                'QH_Ranh giới lập quy hoạch' #do an 2'
                # 'BCP_MD_Xref_Ranhdat$0$BV_Rg_lapquyhoach'   #do an 5
                # 'BTN_MD_Xref_TongThe$0$BV_Rg_lapquyhoach'
                # 'xref_bct2_tong the$0$210129_BConsAnbinh$0$QH_Ranh giới lập quy hoạch' #do an 2
                # 'BTV_MD_Xref_TongThe$0$BV_Rg_lapquyhoach'
            ]
def load_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    return image

def create_mask(image, lower_color, upper_color):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    return mask

def find_contours(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def draw_contours(image, contours, color=(0, 255, 0), thickness=2):
    cv2.drawContours(image, contours, -1, color, thickness)

def label_contours_with_id_and_area(image, contours, areas, scale_factor:float,font_scale=0.5, color=(0, 0, 0), thickness=2):
    """Label contours with both ID and area"""
    for idx, (contour, area) in enumerate(zip(contours, areas)):
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            label = f"ID:{idx+1}\nArea:{(area*scale_factor*scale_factor):.2f}m²"
            y0 = cy
            for i, line in enumerate(label.split('\n')):
                y = y0 + i*50
                cv2.putText(image, line, (cx, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

def compute_pairwise_distances(contours,scale_factor):
    pairwise_distances = []
    for i in range(len(contours)):
        for j in range(i+1, len(contours)):
            points1 = contours[i].reshape(-1, 2)
            points2 = contours[j].reshape(-1, 2)
            if len(points1) == 0 or len(points2) == 0:
                continue
            diff = points1[:, np.newaxis, :] - points2[np.newaxis, :, :]
            squared_dist = np.sum(diff ** 2, axis=2)
            distances = np.sqrt(squared_dist)
            min_idx = (np.unravel_index(np.argmin(distances), distances.shape))
            min_distance = (distances[min_idx]*scale_factor)
            pt1 = tuple(points1[min_idx[0]])
            pt2 = tuple(points2[min_idx[1]])
            pairwise_distances.append({
                'i': i,
                'j': j,
                'distance': min_distance,
                'pt1': pt1,
                'pt2': pt2
            })
    return pairwise_distances

def draw_pairwise_lines(image, pairwise_distances, colors):
    color_idx = 0
    for pd in pairwise_distances:
        line_color = colors[color_idx] if color_idx < len(colors) else (255,255,255)
        cv2.line(image, pd['pt1'], pd['pt2'], line_color, 2)
        mid_x = (pd['pt1'][0] + pd['pt2'][0]) // 2
        mid_y = (pd['pt1'][1] + pd['pt2'][1]) // 2
        label = f"{pd['distance']:.2f} m"
        cv2.putText(image, label, (mid_x, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,0), 3)
        color_idx += 1

def save_image(image, output_path):
    cv2.imwrite(output_path, image)

def print_pairwise_distances(pairwise_distances):
    distance_results = []
    for pd in pairwise_distances:
        distance_text = f"Khoảng cách giữa khối nhà {pd['i']+1} và khối nhà {pd['j']+1} là {pd['distance']:.2f}m"
        distance_results.append(distance_text)
        print(distance_text)
    return distance_results

def format_area_results(contours, areas,scale_factor):
    area_results = []
    for idx, area in enumerate(areas):
        area_text = f"Diện tích của khối nhà {idx+1} là {(area*scale_factor*scale_factor):.2f}m²"
        area_results.append(area_text)
        print(area_text)
    return area_results

def get_filtered_contours(image, lower_yellow, upper_yellow):
    img2 = image.copy()
    hsv_image = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
    center_points = OCR(image)
    print(f"✅ Found {len(center_points)} template matches.")
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    leaf_contours = []
    for i, h in enumerate(hierarchy[0]):
        if h[3] != -1:  # h[2] is First_Child
            leaf_contours.append(contours[i])
    print(f"✅ Found {len(leaf_contours)} leaf contours.")
    filtered_contours = []
    for cnt in leaf_contours:
        for center_point in center_points:
            center_point = (int(center_point[0]), int(center_point[1]))
            inside = cv2.pointPolygonTest(cnt, center_point, True)
            if inside >= 0:  # Point is inside the contour
                filtered_contours.append(cnt)
    if not center_points:
        return leaf_contours # If no template matches, return all leaf contours
    else:
        return filtered_contours

def convert_dxf_to_png(dxf_file, output_dir, target_entity_types, layers_to_extract, bg='#FFFFFF'):
    def get_contour_size(img_dir:str):
        img=cv2.imread(img_dir)
        hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        x, y, w, h = cv2.boundingRect(contours[0])
        return img,w, h

    def get_lwpolyline_bounding_box(lwpolyline):
        try:
            # For LWPOLYLINE, vertices() is a method that returns an iterator
            min_x = float('inf')
            max_x = float('-inf')
            min_y = float('inf')
            max_y = float('-inf')    
            vertices = list(lwpolyline.vertices())
            for vertex in vertices:
                x,y=vertex[:2]
            # Find min/max coordinates
                min_x = min(min_x,x)
                max_x = max(max_x,x)
                min_y = min(min_y,y)
                max_y = max(max_y,y)
            width=max_x-min_x
            height=max_y-min_y
            area = width * height
            bbox= (min_x, min_y, max_x, max_y) 
            return area,height,width,bbox
        
        except Exception as e:
            print(f"Error processing LWPOLYLINE: {e}")
            return None
    def draw_bounding_box(msp, bbox, layer_name="BBOX", color=1):

        min_x, min_y, max_x, max_y = bbox
        # Create rectangle corners
        corners = [
            (min_x, min_y),
            (max_x, min_y),
            (max_x, max_y),
            (min_x, max_y),
            (min_x, min_y)  # Close the rectangle
        ]
        # Add polyline for bounding box
        bbox_polyline = msp.add_lwpolyline(corners)
        bbox_polyline.dxf.layer = layer_name
        bbox_polyline.dxf.color = color
        return bbox_polyline
    
    def fix_dimensions_in_block(doc, block_name):
        block=doc.blocks[block_name]
        for entity in block:
            if entity.dxftype() == 'DIMENSION':
                dim_style = doc.dimstyles.get(entity.dxf.dimstyle)
                if dim_style and hasattr(dim_style.dxf, 'dimpost') and dim_style.dxf.dimpost == 'm':
                    dim_style.dxf.dimpost = "<>m"

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
                    print(f"Error in exploding inserts: {e}")

    def filter_entities(entity):
        """Filter function for matplotlib rendering"""
        return entity.dxftype() in target_entity_types and (entity.dxf.layer in layers_to_extract 
                                                            or entity.dxf.layer.endswith(layers_block[0]))
    # Read DXF and process
    doc = ezdxf.readfile(dxf_file)
    msp = doc.modelspace()
    # Process all INSERT entities
    explode_all_inserts(doc)
    #Draw bbox
    max_height=float()
    max_width=float()
    max_area=0
    max_bbox=tuple()
    for entity in msp:
        if entity.dxftype()=='LWPOLYLINE' and entity.dxf.layer.endswith(layers_rg_qh[0]):
            area,height,width,bbox=get_lwpolyline_bounding_box(entity)
            if area >max_area:
                max_area=area
                max_bbox=bbox
                max_height=height
                max_width=width
    print(f"real height :{max_height},real width:{max_width}, area:{max_area}")
    draw_bounding_box(msp,max_bbox)
    # Render to PNG
    matplotlib.qsave(msp, output_dir,dpi=1400, bg=bg, filter_func=filter_entities,backend='svg')
    output_image,width_pixel,height_pixel=get_contour_size(output_dir)
    #Get the ratio
    scale_factor = height/float(height_pixel)
    print(f"Scale factor is: {scale_factor}")
    return output_image,scale_factor, f'PNG file saved to {output_dir}'   

def OCR(image, custom_config=r'--oem 3 --psm 11'):
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY)
    d = pytesseract.image_to_data(mask, output_type=Output.DICT, config=custom_config, lang='eng')
    n_boxes = len(d['text'])
    center_points = []
    for i in range(n_boxes):
        if d['text'][i] == 'BLOCK':
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            center_points.append((x + w//2, y + h//2))
    if not center_points:
        print("❌ No template matches found.")
    return center_points
def calculate_contour_areas(contours):
    """Calculate areas for each contour"""
    areas = []
    for contour in contours:
        area = cv2.contourArea(contour)
        areas.append(area)
    return areas
def process_single_dxf(dxf_path, output_folder=None):
    """
    Process a single DXF file to calculate shortest distances between contours.
    
    Args:
        dxf_path (str): Path to the DXF file
        output_folder (str, optional): Output folder path. If None, creates folder based on DXF filename
    """
    # Configuration
    lower_yellow = np.array([15, 30, 150])  # Adjusted for lighter yellow
    upper_yellow = np.array([45, 255, 255])
    colors = [(0, 0, 255), (255, 0, 0), (0, 200, 150), (0, 255, 255), (128, 0, 128), 
              (0, 165, 255), (255, 0, 255), (255, 128, 0), (128, 128, 0), (0, 128, 128)]  # Colors for lines
    
    # Validate input file
    if not os.path.exists(dxf_path):
        raise FileNotFoundError(f"DXF file not found at {dxf_path}")
    if not dxf_path.lower().endswith('.dxf'):
        raise ValueError("Input file must be a DXF file")
    
    # Setup output folder
    base_name = os.path.splitext(os.path.basename(dxf_path))[0]
    if output_folder is None:
        output_folder = f"./result_{base_name}"

    # Create output subfolders
    image_folder = os.path.join(output_folder, 'images')
    result_folder = os.path.join(output_folder, 'results')
    
    for folder in [image_folder, result_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    print(f"\nProcessing DXF file: {os.path.basename(dxf_path)}")
    
    # Export image for distance calculation
    output_image_path = os.path.join(image_folder, f"{base_name}.png")
    image, scale_factor, _ =convert_dxf_to_png(dxf_file=dxf_path,output_dir=output_image_path,
                                      target_entity_types=target_entity_types,
                                      layers_to_extract=layers_to_extract)
    print("✅ DXF file processed and images exported.")
    if image is None:
        raise RuntimeError("Failed to load generated images")
    print(f"✅ Loaded images: {base_name}.png and {base_name}_text.png")
    
    # Process the images
    print(f"\nProcessing images for: {base_name}")
    output_image = image.copy()
    filtered_contours = get_filtered_contours(image, lower_yellow, upper_yellow)
    
    # Calculate areas
    contour_areas = calculate_contour_areas(filtered_contours)
    # Draw contours and label them with IDs
    draw_contours(output_image, filtered_contours, color=(0, 255, 0), thickness=2)
    label_contours_with_id_and_area(output_image, 
                                    filtered_contours,
                                    contour_areas,scale_factor,font_scale=1.5, color=(0, 0, 0), thickness=2)
    # Compute and visualize pairwise distances
    pairwise_distances = compute_pairwise_distances(filtered_contours,scale_factor)
    draw_pairwise_lines(output_image, pairwise_distances, colors)
    # Save output image
    output_filename = f"output_{base_name}.png"
    output_path = os.path.join(result_folder, output_filename)
    save_image(output_image, output_path)
    print(f"✅ Saved result to: {output_path}")
    # Format results
    print("\n📏 Distance Results:")
    distance_results = print_pairwise_distances(pairwise_distances)
    area_results = format_area_results(filtered_contours, contour_areas,scale_factor)
    return {
        'output_path': output_path,
        'distance_pairwise': distance_results,
        'area': area_results,
        'contours_count': len(filtered_contours)
    }
if __name__ == "__main__":
    # Example usage for single DXF file
    dxf_file_path = './cad_to_png/dxf/Ti_le/do_an_8.dxf'  
    output_folder = './cad_to_png/png/Khoang_cach_result'  # Replace with your desired output folder (optional)
    result = process_single_dxf(dxf_file_path, output_folder)
        