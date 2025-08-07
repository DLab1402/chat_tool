import ezdxf
from ezdxf.entities import Dimension
import numpy as np
from ezdxf.addons.drawing import matplotlib
layer_dat_nha_o='QH_DAT_NO_Nhaochungcu'
layer_ranh_gioi_lap_quy_hoach=['QH_Ranh giới lập quy hoạch',
                               'BV_Rg_lapquyhoach']
layer_to_extract=['QH_DAT_NO_Nhaochungcu',
                  '2_Visible_line',
                  'QHDH_DAT_CTHTKT_DuongGT_CH',
                  'QH_DAT_Cayxanhhanche'
]
# 3========================================D 
def decode_dimtype(dimtype_value):
    """
    Decode the dimtype value to extract base dimension type and flags.
    
    Args:
        dimtype_value (int): The raw dimtype value from DXF
    
    Returns:
        dict: Dictionary containing decoded information
    """
    # Extract base dimension type (lower 4 bits)
    base_type = dimtype_value & 0x0F
    
    # Common dimension type names
    type_names = {
        0: "Linear/Rotated",
        1: "Aligned", 
        2: "Angular",
        3: "Diameter",
        4: "Radius",
        5: "Angular 3-point",
        6: "Ordinate"
    }
    # Extract flags (higher bits)
    flags = []
    if dimtype_value & 0x20:  # Bit 5
        flags.append("Block reference")
    if dimtype_value & 0x40:  # Bit 6
        flags.append("Ordinate type")
    if dimtype_value & 0x80:  # Bit 7
        flags.append("Text positioned manually")
    if dimtype_value & 0x100:  # Bit 8
        flags.append("Unknown flag 8")
    return {
        'raw_value': dimtype_value,
        'base_type': base_type,
        'type_name': type_names.get(base_type, f"Unknown type {base_type}"),
        'flags': flags,
        'binary': bin(dimtype_value)
    }
# 3========================================D
def get_needed_dim(dxf_file_path):
    """
    Extract only aligned dimensions from a specific layer.
    
    Args:
        dxf_file_path (str): Path to the DXF file
        target_layer (str): Layer name to extract dimensions from
        debug (bool): Enable debug output
    
    Returns:
        list: List of aligned dimensions only
    """
    all_dimensions = extract_dimensions_from_layer(dxf_file_path)
    if not all_dimensions:
        return []
    dims=[]
    for i,dim in enumerate(all_dimensions['mep_duong']):
        dims.append(dim)
    for i, dim in enumerate(all_dimensions['duong_nb']):
        dims.append(dim)
    return dims
def fix_dimensions_in_block(doc, block_name):
        block=doc.blocks[block_name]
        for entity in block:
            if entity.dxftype() == 'DIMENSION':
                dim_style = doc.dimstyles.get(entity.dxf.dimstyle)
                if dim_style and hasattr(dim_style.dxf, 'dimpost') and dim_style.dxf.dimpost == 'm':
                    dim_style.dxf.dimpost = "<>m"
    # 3========================================D
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

# 3========================================D
def extract_dimensions_from_layer(dxf_file_path):
    """
    Extract aligned and rotated dimensions from a specific layer in a DXF file.
    Args:
        dxf_file_path (str): Path to the DXF file
        target_layer (str): Layer name to extract dimensions from (default: "1_Fine line")
        debug (bool): Enable debug output
    
    Returns:
        dict: Dictionary containing aligned and rotated dimensions with their properties
    """
    try:
        # Load the DXF file
        doc = ezdxf.readfile(dxf_file_path)
        msp = doc.modelspace()
        explode_all_inserts(doc)  # Explode all inserts to ensure dimensions are accessible
        # Dictionary to store extracted dimensions
        extracted_dimensions = {
            'duong_nb': [],
            'mep_duong':[]
        }
        # Debug counters
        duong_nb = 0
        mep_duong= 0
        dims=[]
        duong_nha_o=[]
        duong_rg_lapquyhoach=[]                      
        # Iterate through all entities in the modelspace
        for entity in msp:
            if entity.dxftype() == 'DIMENSION':             #modify the layer name to match your DXF file
                    dims.append(entity)
                    dim_style = doc.dimstyles.get(entity.dxf.dimstyle)
                    if dim_style and hasattr(dim_style.dxf, 'dimpost') and dim_style.dxf.dimpost == 'm':
                        dim_style.dxf.dimpost = "<>m"
            elif entity.dxftype()=='LWPOLYLINE' and entity.dxf.layer.endswith(layer_dat_nha_o):
                    duong_nha_o.append(entity)
            elif entity.dxftype()=='LWPOLYLINE' and (entity.dxf.layer.endswith(layer_ranh_gioi_lap_quy_hoach[0]) 
                                                     or entity.dxf.layer.endswith(layer_ranh_gioi_lap_quy_hoach[1])):
                duong_rg_lapquyhoach.append(entity)
        dims_inside_ranh_gioi_lap_quy_hoach = get_dim_inside_ranh_dat(dims,duong_rg_lapquyhoach)
        for dim in dims_inside_ranh_gioi_lap_quy_hoach:
            # Check if the dimension is aligned or rotated
            dimtype = getattr(dim.dxf, 'dimtype', 'Unknown')
            decoded_dimtype = None
            if isinstance(dimtype, int):
                decoded_dimtype = decode_dimtype(dimtype)                                                                                                                                                                                                                                                                                                            
            # Extract properties only if decode successful
            if decoded_dimtype:
                base_dimtype = decoded_dimtype['base_type']
                if base_dimtype == 0 or base_dimtype == 1:  # Aligned or Rotated dimensions
                    dim_points = get_dim_points(dim) # Check if any point is inside any LWPOLYLINE on the target layer
                    dimension_classified = False # Flag to track if this dimension has been classified
                    # Check each point against all polylines
                    for point in dim_points:
                          # Skip remaining points if already classified 
                        for lwpoly in duong_nha_o:
                            if check_point_in_dat_nha_o_line(point, lwpoly):
                                extracted_dimensions['mep_duong'].append(extract_dimension_properties(dim))
                                mep_duong += 1
                                dimension_classified = True
                                break  # Break inner loop once classified
                        if dimension_classified:
                            break
                    # If no point was inside any polyline, classify as duong_nb
                    if not dimension_classified:
                        extracted_dimensions['duong_nb'].append(extract_dimension_properties(dim))
                        duong_nb += 1
            if dim.dxf.layer not in layer_to_extract:
                layer_to_extract.append(dim.dxf.layer)  # Add layer to extract if not already present
        print(f"Total dimension entities found: {len(dims)}")
        print(f"Tong duong nha o: {len(duong_nha_o)}")
        print(f"Tong mep duong dimensions found: {mep_duong}")    
        print(f"so ky hieu chieu rong duong noi bo: {duong_nb}")
    except ezdxf.DXFStructureError as e:
        print(f"Error reading DXF file: {e}")
        return None
    return extracted_dimensions

def check_point_in_dat_nha_o_line(point, duong_dat_nha_o,tolerance=0.1):
    """
    Check if a point is ON the boundary of a closed LWPOLYLINE (not inside).
    
    Args:
        point: Point to check
        duong_dat_nha_o: LWPOLYLINE entity
        tolerance: Distance tolerance for considering a point "on" the boundary
    
    Returns:
        bool: True if point is ON the boundary (not inside)
    """
    # Get vertices from LWPOLYLINE
    vertices = [(vertex[0], vertex[1]) for vertex in duong_dat_nha_o.vertices_in_wcs()]
    
    x, y = point.x, point.y
    n = len(vertices)
    
    # Check if point is exactly on any vertex
    for vx, vy in vertices:
        distance = ((x - vx) ** 2 + (y - vy) ** 2) ** 0.5
        if distance <= tolerance:
            return True
    
    # Check if point is on any edge of the polyline
    for i in range(n):
        v1 = vertices[i]
        v2 = vertices[(i + 1) % n]
        
        if point_on_line_segment_with_tolerance(x, y, v1[0], v1[1], v2[0], v2[1], tolerance):
            return True
    
    return False
def point_on_line_segment_with_tolerance(px, py, x1, y1, x2, y2, tolerance=0.1):
    """
    Check if a point is on a line segment within a given tolerance.
    
    Args:
        px, py: Point coordinates
        x1, y1, x2, y2: Line segment endpoints
        tolerance: Distance tolerance
    
    Returns:
        bool: True if point is on the line segment within tolerance
    """
    # Calculate the distance from point to line segment
    A = px - x1
    B = py - y1
    C = x2 - x1
    D = y2 - y1
    dot = A * C + B * D
    len_sq = C * C + D * D
    
    if len_sq == 0:  # Line segment is actually a point
        distance = (A * A + B * B) ** 0.5
        return distance <= tolerance
    
    param = dot / len_sq
    
    if param < 0:
        # Point is closest to start of segment
        xx = x1
        yy = y1
    elif param > 1:
        # Point is closest to end of segment
        xx = x2
        yy = y2
    else:
        # Point is closest to somewhere on the segment
        xx = x1 + param * C
        yy = y1 + param * D
    
    # Calculate distance from point to closest point on segment
    dx = px - xx
    dy = py - yy
    distance = (dx * dx + dy * dy) ** 0.5
    
    return distance <= tolerance
def get_dim_inside_ranh_dat(dimension_entities, ranh_dat):
    dims=[]
    for dimension_entity in dimension_entities:
        mid_point=dimension_entity.dxf.text_midpoint
        for lwpoly in ranh_dat:
            min_x = float('inf')
            max_x = float('-inf')
            min_y = float('inf')
            max_y = float('-inf')    
            vertices = list(lwpoly.vertices())
            for vertex in vertices:
                x,y=vertex[:2]
            # Find min/max coordinates
                min_x = min(min_x,x)
                max_x = max(max_x,x)
                min_y = min(min_y,y)
                max_y = max(max_y,y)
            # Check if the midpoint is inside the bounding box of the LWPOLYLINE
            dimension_classified = False
            if (min_x <= mid_point.x <= max_x) and (min_y <= mid_point.y <= max_y):
                # If inside, extract points and properties
                dims.append(dimension_entity)
                dimension_classified = True
                break
            if dimension_classified:
                break
    return dims
def get_dim_points(dimension_entity):
    """
    Extract points from a dimension entity.
    
    Args:
        dimension_entity: ezdxf dimension entity
    
    Returns:
        list: List of points (tuples) extracted from the dimension
    """
    points = []
    for key in ['defpoint', 'defpoint2', 'defpoint3', 'text_midpoint']:
        pt = getattr(dimension_entity.dxf, key, None)
        if pt is not None:
            points.append(pt)
    return points
# 3========================================D
def extract_dimension_properties(dimension_entity):
    """
    Extract properties from a dimension entity.
    Args:
        dimension_entity: ezdxf dimension entity
        debug (bool): Enable debug output
    Returns:
        dict: Dictionary containing dimension properties
    """
    dim_props = {
        'handle': dimension_entity.dxf.handle,
        'layer': dimension_entity.dxf.layer,
        'dimtype': dimension_entity.dxf.dimtype,
        'measurement': getattr(dimension_entity.dxf, 'actual_measurement', None),
        'text': getattr(dimension_entity.dxf, 'dimension_text', ''),
        'defpoint': getattr(dimension_entity.dxf, 'defpoint', None),
        'defpoint2': getattr(dimension_entity.dxf, 'defpoint2', None),
        'defpoint3': getattr(dimension_entity.dxf, 'defpoint3', None),
        'text_midpoint': getattr(dimension_entity.dxf, 'text_midpoint', None),
        'angle': getattr(dimension_entity.dxf, 'angle', 0),
        'oblique_angle': getattr(dimension_entity.dxf, 'oblique_angle', 0),
    }
    # Add color and linetype if available
    if hasattr(dimension_entity.dxf, 'color'):
        dim_props['color'] = dimension_entity.dxf.color
    if hasattr(dimension_entity.dxf, 'linetype'):
        dim_props['linetype'] = dimension_entity.dxf.linetype
    return dim_props
# 3========================================D
def print_dimension_summary(dimensions_data):
    """
    Print a summary of extracted dimensions.
    
    Args:
        dimensions_data (dict): Dictionary containing extracted dimensions
    """
    results=[]
    if not dimensions_data:
        print("No dimensions data to display.")
        return
    duong_nb = len(dimensions_data['duong_nb'])
    mep_duong = len(dimensions_data['mep_duong'])
    # Print details of aligned dimensions
    if duong_nb > 0:
        print(f"\n--- Duong nb ---")
        for i, dim in enumerate(dimensions_data['duong_nb'], 1):
            results.append(f"  Ký hiệu độ rộng đường nội bộ số {i} có kích thước là: {(dim['measurement']):.2f}m")
            print(f"  Ký hiệu độ rộng đường nội bộ số {i} có kích thước là: {(dim['measurement']):.2f}m")
    else:
        print(f"\n--- Duong nb ---")
        print("Không tìm thấy bất kỳ ký hiệu độ rộng đường nội bộ nào.")
    # Print details of rotated dimensions
    if mep_duong > 0:
        print(f"\n--- mep_duong ---")
        for i, dim in enumerate(dimensions_data['mep_duong'], 1):
            results.append(f"  Ký hiệu khoảng cách từ tường nhà tới mép đường số {i+duong_nb} có kích thước là: {(dim['measurement']):.2f}m")
            print(f"  Ký hiệu khoảng cách từ tường nhà tới mép đường số {i+duong_nb} có kích thước là: {(dim['measurement']):.2f}m")
    else:
        print(f"\n--- mep_duong ---")
        print("Không tìm thấy bất kỳ ký hiệu khoảng cách từ tường nhà tới mép đường nào.")
    return results
def annotate_dimensions(dims,msp,index=1):
    for i, dim in enumerate(dims):
        # Get the dimension points
        pts = []
        for key in ['defpoint', 'defpoint2', 'defpoint3', 'text_midpoint']:
            pt = dim.get(key)
            if pt is not None:
                pts.append((pt[0], pt[1]))
        if len(pts) < 2:
            continue  # Not enough points to form a rectangle
        pts_np = np.array(pts)
        min_x, min_y = pts_np.min(axis=0)
        max_x, max_y = pts_np.max(axis=0)
        # Create a rectangle around the dimension points
        msp.add_text(
                text=index+i,
                dxfattribs={'height': 2, 'layer': 'bounding_box', 'color': 1, 
                            'style': 'Standard',
                            'insert':(min_x, min_y), 
                            'rotation': 0,
                            'lineweight':100}
            )
# 3========================================D
def main(dxf_file_path,output_path):
    """
    Main function to extract aligned dimensions from a DXF file and save them with bounding boxes.
    Args:
        dxf_file_path (str): Path to the DXF file
        output_path (str): Path to save the output DXF with bounding boxes
    """ 
    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace() 
    # Get only aligned dimensions
    all_dims=extract_dimensions_from_layer(dxf_file_path)
    results=print_dimension_summary(all_dims)
    mep_duong=all_dims['mep_duong']
    do_rong_duong_nb=all_dims['duong_nb']
    # Create a new layer for bounding boxes
    if "bounding_box" not in doc.layers:
        doc.layers.new(name="bounding_box", dxfattribs={'color': 1})
    if do_rong_duong_nb:
        print(f"\n✅ SUCCESS: Found {len(do_rong_duong_nb)} duong nb dimensions!")
        annotate_dimensions(do_rong_duong_nb, msp, index=1)    
    if mep_duong:
        print(f"\n✅ SUCCESS: Found {len(mep_duong)} mep duong dimensions!")
        annotate_dimensions(mep_duong, msp, index=len(do_rong_duong_nb)+1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
        # Save the new DXF with bounding boxes
    for layer in doc.layers:
        if (layer.dxf.name.endswith(tuple(layer_to_extract)) 
            # or layer.dxf.name.endswith(layer_to_extract[1]) 
            # or layer.dxf.name.endswith(layer_to_extract[2]) 
            # or layer.dxf.name.endswith(layer_to_extract[3])
            # or layer.dxf.name.endswith(layer_to_extract[6]) 
            or layer.dxf.name == layer_dat_nha_o
            or layer.dxf.name=='bounding_box'):
            layer.on()
        else:              
            layer.off()
    print("✅ All layers are set to ON for extraction.")
    matplotlib.qsave(doc.modelspace(), output_path,dpi=600, bg="#FFFFFF")
    return results

# Example usage
if __name__ == "__main__":
    # Replace with your DXF file path
    dxf_file_path = "./cad_to_png/dxf/Ti_le/do_an_2.dxf"
    output_path="./cad_to_png/do_an_bind_2.png"
    main(dxf_file_path, output_path)