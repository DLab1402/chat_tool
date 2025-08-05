import ezdxf
from ezdxf.addons.drawing import matplotlib
import os 
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
bg='#FFFFFF'

def convert_GTNB(layers_to_extract, layer_GTNB, doc, output_folder, binary):  
    msp = doc.modelspace()
    explode_all_inserts(doc)
    if binary:
        for entity in msp:
            if entity.dxftype() == 'HATCH' and entity.dxf.layer == layer_GTNB:
                print('Có hatch cho đường nội bộ')
                entity.set_solid_fill(color=7,style=1)

        for layer in doc.layers:
            if layer.dxf.name not in layers_to_extract:
                layer.off()
            else:
                layer.on()
        output_dir = os.path.join(output_folder, "hatch_task2.png")
        matplotlib.qsave(msp, output_dir,dpi=200, bg=bg)
    else:
        for entity in msp:
            if entity.dxftype() == 'HATCH' and entity.dxf.layer == layer_GTNB:
                print('Có hatch cho đường nội bộ')
                entity.set_pattern_fill(name="ANSI31", color=8, scale=2.0, angle=0, style=1)

        for layer in doc.layers:
            if layer.dxf.name not in layers_to_extract:
                layer.off()
            else:
                layer.on()
        output_dir = os.path.join(output_folder, "origin_task2.png")
        matplotlib.qsave(msp, output_dir,dpi=200, bg=bg)