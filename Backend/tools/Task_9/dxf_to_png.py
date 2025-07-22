from ezdxf.addons.drawing import matplotlib
from pathlib import Path

def convert_dxf_to_png(doc, output_path, layers_to_check, dpi=300, output_prefix=""):
    """Process a single DXF file and export its modelspace to PNG in output_folder."""

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

    if not doc:
        return

    toggle_layers(doc, layers_to_check)

    export_to_png(doc.modelspace(), output_path, dpi)

    print("\n✅ DXF file processing complete.")