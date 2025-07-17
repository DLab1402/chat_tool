import sys
import ezdxf
from ezdxf.addons.drawing import matplotlib
import os
from pathlib import Path

def ensure_output_folder_exists(folder):
    """Ensure the output folder exists."""
    Path(folder).mkdir(parents=True, exist_ok=True)

def get_dxf_files(folder):
    """Get all DXF files in the input folder."""
    return [f for f in os.listdir(folder) if f.lower().endswith('.dxf')]

def read_dxf_file(dxf_path):
    """Read a DXF file and return the document object."""
    try:
        doc = ezdxf.readfile(dxf_path)
        return doc
    except IOError:
        print(f"❌ File not found or cannot be opened: {dxf_path}")
    except ezdxf.DXFStructureError:
        print(f"❌ Invalid or corrupted DXF file: {dxf_path}")
    return None

def toggle_layers(doc, layers_to_check):
    """Check if all specified layers exist and toggle layers in the DXF file."""
    layers = doc.layers
    missing_layers = [layer for layer in layers_to_check if layer not in layers]
    if missing_layers:
        print(f"❌ The following layers do not exist: {', '.join(missing_layers)}")
    else:
        print(f"✅ All specified layers exist: {', '.join(layers_to_check)}")
    
    for layer in layers:
        if layer.dxf.name not in layers_to_check:
            layer.off()
        else:
            layer.on()

def export_to_png(layout, output_path, dpi):
    """Export a layout to PNG."""
    try:
        matplotlib.qsave(layout, output_path, dpi=dpi, bg="#FFFFFF", size_inches=(46.81, 33.12))
        print(f"✅ Exported as PNG: {output_path}")
    except Exception as e:
        print(f"❌ Failed to export as PNG: {e}")

def process_dxf_file(dxf_file, input_folder, output_folder, layers_to_check, output_filename, dpi):
    """Process a single DXF file."""
    dxf_path = os.path.join(input_folder, dxf_file)
    print(f"\nProcessing: {dxf_file}")

    # Read the DXF file
    doc = read_dxf_file(dxf_path)
    if not doc:
        return

    # Toggle layers
    toggle_layers(doc, layers_to_check)

    # Use fixed output filename
    output_path = os.path.join(output_folder, output_filename)

    # Check layouts
    layouts = doc.layouts
    layout_names = [layout.dxf.name for layout in layouts]
    if layout_names:
        layout = layouts.get(layout_names[1])  # Use the second layout if it exists
        if len(list(layout)) > 0:
            print(f"✅ Layout '{layout_names[1]}' exists and has entities - Exporting to PNG.")
            export_to_png(layout, output_path, dpi)
        else:
            print(f"❌ Layout '{layout_names[1]}' exists but has no entities - Exporting from modelspace.")
            export_to_png(doc.modelspace(), output_path, dpi)
    else:
        print(f"❌ No layouts found - Exporting from modelspace.")
        export_to_png(doc.modelspace(), output_path, dpi)

def convert_dxf_to_png(input_folder, output_folder, layers_to_check, output_filename="png.png", dpi=300):
    """Convert DXF files to PNG with specified layers and fixed output filename."""
    ensure_output_folder_exists(output_folder)
    dxf_files = get_dxf_files(input_folder)

    if not dxf_files:
        print("❌ No DXF files found in the input folder.")
        return

    for dxf_file in dxf_files:
        process_dxf_file(dxf_file, input_folder, output_folder, layers_to_check, output_filename, dpi)

    print("\n✅ Processing complete.")
