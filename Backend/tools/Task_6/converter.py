import ezdxf
from ezdxf.addons.drawing import matplotlib
import os
from pathlib import Path

def convert_dxf_to_png(doc, output_folder, layers_to_check, dpi=300, output_prefix=""):
    """Process a single DXF file and export its modelspace to PNG in output_folder."""
    
    def ensure_output_folder_exists(folder):
        Path(folder).mkdir(parents=True, exist_ok=True)


    def toggle_layers(doc, layers_to_check):
        layers = doc.layers
        missing_layers = [layer for layer in layers_to_check if layer not in layers]
        if missing_layers:
            print(f"❌ The following layers do not exist: {', '.join(missing_layers)}")
        else:
            print(f"✅ All specified layers exist: {', '.join(layers_to_check)}")

        for layer in doc.layers:
            if layer.dxf.name not in layers_to_check:
                layer.off()
            else:
                layer.on()

    def export_to_png(layout, output_path, dpi):
        try:
            matplotlib.qsave(layout, output_path, dpi=dpi, bg="#FFFFFF", size_inches=(46.81, 33.12))
            print(f"✅ Exported as PNG: {output_path}")
        except Exception as e:
            print(f"❌ Failed to export as PNG: {e}")

    # Bắt đầu xử lý
    ensure_output_folder_exists(output_folder)

    if not doc:
        return

    toggle_layers(doc, layers_to_check)

    # Tạo tên file PNG
    output_filename = f"PNG.png"
    output_path = os.path.join(output_folder, output_filename)

    export_to_png(doc.modelspace(), output_path, dpi)

    print("\n✅ DXF file processing complete.")
