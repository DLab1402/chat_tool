import os
from typing import Dict, List

# Mapping giữa task và mã QH cần dùng
TASK_QH_MAPPING = {
    "task1": "QH02",
    "task2": "QH03",
    "task3": "PDF",
    "task4": "QH02",
    "task5": "QH03",
    "task6": "QH03",
    "task9": "QH06",
    "task10": "QH06",
    "task11": "PDF",
    "task12": "QH02",
    "task13": "QH09"
}

def classify_input_files(input_folder: str) -> Dict[str, List[str]]:
    files = os.listdir(input_folder)
    result = {task: [] for task in TASK_QH_MAPPING}
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    pdf_path = os.path.join(input_folder, pdf_files[0]) if len(pdf_files) == 1 else None

    for file in files:
        if file.lower().endswith('.dxf'):
            for task, qh_code in TASK_QH_MAPPING.items():
                if qh_code.startswith("QH") and file.upper().startswith(qh_code):
                    result[task].append(os.path.join(input_folder, file))
    
    # Chỉ gán PDF cho các task thực sự cần PDF
    if pdf_path:
        result["task3"] = [pdf_path]
        result["task11"] = [pdf_path]
    return result

# Ví dụ sử dụng:
if __name__ == "__main__":
    input_dir = r"d:\LAB\Backend\session\input"
    classified = classify_input_files(input_dir)
    for task, files in classified.items():
        print(f"{task}:")
        for f in files:
            print(f"  {f}")