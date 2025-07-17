import ezdxf
from ezdxf.entities import Dimension
import numpy as np
from ezdxf.addons.drawing import matplotlib
import cv2

layer_mep_duong='Chieu_rong_mep_duong'
layer_to_extract=['QH_DAT_NO_Nhaochungcu','2_Visible_line','QHDH_DAT_CTHTKT_DuongGT_CH','QH_Ranh giới lập quy hoạch','VTD_Bang toa do']

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
        inserts=msp.query('INSERT')
        # Dictionary to store extracted dimensions
        extracted_dimensions = {
            'duong_nb': [],
            'mep_duong':[]
        }
        # Debug counters
        dimension_entities = 0
        duong_nb = 0
        mep_duong= 0
        # Iterate through all entities in the modelspace
        for insert in inserts:
            block = doc.blocks[insert.dxf.name]
            for entity in block:
                if entity.dxftype() == 'DIMENSION':
                    try:
                        dimension_entities += 1
                        dimtype = getattr(entity.dxf, 'dimtype', 'Unknown')
                        angle = getattr(entity.dxf, 'angle', 0)
                        dim_style = doc.dimstyles.get(entity.dxf.dimstyle)
                        
                        # Initialize decoded_dimtype before use
                        decoded_dimtype = None
                        if isinstance(dimtype, int):
                            decoded_dimtype = decode_dimtype(dimtype)
                        
                        if dim_style and hasattr(dim_style.dxf, 'dimpost') and dim_style.dxf.dimpost == 'm':
                            dim_style.dxf.dimpost = "<>m"
                        
                        # Extract properties only if decode successful
                        if decoded_dimtype:
                            dim_data = extract_dimension_properties(entity)
                            base_dimtype = decoded_dimtype['base_type']
                            
                            # Classify dimensions
                            if base_dimtype == 1 or base_dimtype==0:
                                if entity.dxf.layer!=layer_mep_duong: 
                                    extracted_dimensions['duong_nb'].append(dim_data)
                                    duong_nb += 1
                                elif entity.dxf.layer==layer_mep_duong:
                                    extracted_dimensions['mep_duong'].append(dim_data)
                                    mep_duong+=1
                    except Exception as e:
                        print(f"Error processing dimension: {e}")
                        continue
        #print(f"Total dimension entities found: {dimension_entities}")
        #print(f"Tong mep duong dimensions found: {mep_duong}")    
        #print(f"so ky hieu chieu rong duong noi bo: {duong_nb}")
    except ezdxf.DXFStructureError as e:
        print(f"Error reading DXF file: {e}")
        return None
    return extracted_dimensions
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

def print_dimension_summary(dimensions_data):
    """
    Print a summary of extracted dimensions.
    
    Args:
        dimensions_data (dict): Dictionary containing extracted dimensions
    """
    result = {"Đường nội bộ": [],"Mép": []}

    duong = []
    mep = []
    if not dimensions_data:
        #print("No dimensions data to display.")
        return
    
    duong_nb = len(dimensions_data['duong_nb'])
    mep_duong = len(dimensions_data['mep_duong'])
    #print(f"\n=== Dimension Extraction Summary ===")
    #print(f"duong nb dimensions found: {duong_nb}")
    #print(f"mep duong dimensions found: {mep_duong}")
    #print(f"Total dimensions: {duong_nb +mep_duong}")
    # Print details of aligned dimensions
    if duong_nb > 0:
        #print(f"\n--- Duong nb ---")
        for i, dim in enumerate(dimensions_data['duong_nb'], 1):
            duong.append(f"  Ký hiệu độ rộng đường nội bộ số {i} có kích thước là: {(dim['measurement']):.2f}m")
            #print(f"  Ký hiệu độ rộng đường nội bộ số {i} có kích thước là: {(dim['measurement']):.2f}m")
        
        result["Đường nội bộ"] = duong
    # Print details of rotated dimensions
    if mep_duong > 0:
        #print(f"\n--- mep_duong ---")
        for i, dim in enumerate(dimensions_data['mep_duong'], 1):
            mep.append(f"  Ký hiệu độ rộng mép đường {i+duong_nb} có kích thước là: {(dim['measurement']):.2f}m")
            #print(f"  Ký hiệu độ rộng mép đường {i+duong_nb} có kích thước là: {(dim['measurement']):.2f}m")

        result["Mép"] = mep

    return result
def explode_dimension(doc):
    msp=doc.modelspace()
    inserts=msp.query('INSERT')
    for insert in inserts:
        block=doc.blocks[insert.dxf.name]
        #Fix dimstyle 
        for block_entity in block:
            if block_entity.dxftype()=='DIMENSION':
                dim_style = doc.dimstyles.get(block_entity.dxf.dimstyle)
                if dim_style and hasattr(dim_style.dxf, 'dimpost') and dim_style.dxf.dimpost == 'm':
                    dim_style.dxf.dimpost = "<>m"
        
def main(dxf_file_path, process_folder = None, output_folder = None, output_name = "Task_4.png"):
    """
    Main function to extract aligned dimensions from a DXF file and save them with bounding boxes.
    Args:
        dxf_file_path (str): Path to the DXF file
        output_path (str): Path to save the output DXF with bounding boxes
    """

    output_folder += f"/{output_name}"
    process_folder += f"/{output_name}"

    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace()
    # Get only aligned dimensions
    all_dims=extract_dimensions_from_layer(dxf_file_path)
    results=print_dimension_summary(all_dims)
    do_rong_duong_dimensions = get_needed_dim(dxf_file_path)

    # Create a new layer for bounding boxes
    if "bounding_box" not in doc.layers:
        doc.layers.new(name="bounding_box", dxfattribs={'color': 1})
    
    if do_rong_duong_dimensions:
        #print(f"\n✅ SUCCESS: Found {len(do_rong_duong_dimensions)} aligned dimensions!")
        # Process each aligned dimension
        for i, dim in enumerate(do_rong_duong_dimensions):
            pts = []
            for key in ['defpoint', 'defpoint2', 'defpoint3', 'text_midpoint']:
                pt = dim.get(key)
                if pt is not None:
                    pts.append((pt[0], pt[1]))
            if len(pts) < 2:
                continue  # Not enough points
            
            pts_np = np.array(pts)
            min_x, min_y = pts_np.min(axis=0)
            max_x, max_y = pts_np.max(axis=0)

            # Rectangle corners
            rect = [
                (min_x-2, min_y-2),
                (max_x+2, min_y-2),
                (max_x+2, max_y+2),
                (min_x-2, max_y+2),
                (min_x-2, min_y-2)  # Close the rectangle
            ]
            # Draw rectangle as LWPOLYLINE
            msp.add_lwpolyline(rect, dxfattribs={'layer': 'bounding_box', 'color': 3, 'closed': True,'lineweight': 100})
            msp.add_text(
                text=i+1,
                dxfattribs={'height': 2, 'layer': 'bounding_box', 'color': 1, 
                            'style': 'Standard',
                            'insert':(max_x, max_y), 
                            'rotation': 0,
                            'lineweight':500}
            )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
        # Save the new DXF with bounding boxes
        for layer in doc.layers:
            if (layer.dxf.name.endswith(layer_to_extract[0]) 
                or layer.dxf.name.endswith(layer_to_extract[1]) 
                or layer.dxf.name.endswith(layer_to_extract[2]) 
                or layer.dxf.name.endswith(layer_to_extract[3])
                or layer.dxf.name.endswith(layer_to_extract[4]) 
                or layer.dxf.name == layer_mep_duong
                or layer.dxf.name=='bounding_box'):
                layer.on()
            else:              
                layer.off()
        layouts = doc.layouts
        layout_names = [layout.dxf.name for layout in layouts]
        if layout_names:
            layout = layouts.get(layout_names[1])  # Use the second layout if it exists
            if len(list(layout)) > 0:
                #print(f"✅ Layout '{layout_names[1]}' exists and has entities - Exporting to PNG.")
                matplotlib.qsave(layout, process_folder, dpi=300, bg="#FFFFFF")
            else:
                #print(f"❌ Layout '{layout_names[1]}' exists but has no entities - Exporting from modelspace.")
                matplotlib.qsave(doc.modelspace(), process_folder,dpi=300, bg="#FFFFFF")
        else:
            #print(f"❌ No layouts found - Exporting from modelspace.")
            matplotlib.qsave(doc.modelspace(), process_folder, size_inches=(16.5,11.6), bg="#FFFFFF")
   

    results["image"] = cv2.imread(process_folder)
    cv2.imwrite(output_folder,results["image"])
    
    return results