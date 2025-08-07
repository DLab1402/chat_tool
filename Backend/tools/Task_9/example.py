from converter import draw_trucuuhoa_distances
import os

# Lấy danh sách file trong folder 'input'
input_folder = "input"
output_folder = "output"

dxf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.dxf')]

if not dxf_files:
    print("Không tìm thấy file DXF nào trong folder 'input'. Vui lòng thêm file vào.")
else:
    # Lấy file đầu tiên
    input_file = os.path.join(input_folder, dxf_files[0])

    # Tạo tên file output tương ứng
    output_file = os.path.join(output_folder, "trucuuhoa_distances.png")

    # Gọi hàm xử lý
    draw_trucuuhoa_distances(input_file, output_file)
