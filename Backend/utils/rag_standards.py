# rag_standards.py
"""
Module lưu trữ và truy xuất quy chuẩn kỹ thuật cho các task đối chiếu.
Có thể mở rộng sang file/text/vector DB trong tương lai.
"""

from typing import List, Dict
import re

# Danh sách quy chuẩn ban đầu (có thể bổ sung sau)
STANDARDS = [
    {
        "task": "task4",
        "question": "Khoảng cách từ mép đường tới tường nhà, công trình",
        "standard": "Khoảng cách từ mép đường cho xe chữa cháy đến tường của ngôi nhà phải không lớn hơn 5 m đối với các nhà có chiều cao nhỏ hơn 12 m, không lớn hơn 8 m đối với các nhà có chiều cao trên 12 m đến 28 m và không lớn hơn 10 m đối với các nhà có chiều cao trên 28 m. Trong những trường hợp cần thiết, khoảng cách từ mép gần nhà của đường xe chạy đến tường ngoài của ngôi nhà và công trình được tăng đến 60 m với điều kiện ngôi nhà và công trình này có các đường cụt vào, kèm theo bãi quay xe chữa cháy và bố trí các trụ nước chữa cháy. Trong trường hợp đó, khoảng cách từ nhà và công trình đến bãi quay xe chữa cháy phải không nhỏ hơn 5 m và không lớn hơn 15 m và khoảng cách giữa các đường cụt không được vượt quá 100 m.",
        "article": "Điều 6.2.2.3 QCVN 06:2022/BXD"
    }
]

def search_standard(task: str = None, query: str = None) -> Dict:
    """
    Truy xuất quy chuẩn phù hợp nhất dựa trên task hoặc query.
    Nếu có task, ưu tiên tìm theo task. Nếu không, tìm theo query (tìm kiếm keyword).
    """
    if task:
        for std in STANDARDS:
            if std.get("task") == task:
                return std
    if query:
        # Tìm quy chuẩn có keyword gần giống query
        for std in STANDARDS:
            if re.search(query, std.get("question", ""), re.IGNORECASE):
                return std
    return None
