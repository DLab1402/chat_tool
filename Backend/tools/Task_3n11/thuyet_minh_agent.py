import os
import re
import requests
import json
import pdfplumber
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.global_var import AGENT_API_KEY

PDF_PATH = "input.pdf"  # Giá trị này sẽ được thay bằng file tạm khi gọi từ MCP server

import sys

# from utils.global_var import AGENT_API_KEY
API_KEY = AGENT_API_KEY

GEMINI_MODEL = "models/gemini-1.5-pro"

def extract_sections_by_titles(pdf_path, section_titles):
    """
    Trích xuất nội dung các section theo danh sách tiêu đề.
    Trả về dict {section_title: content}
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    pattern = "(" + "|".join(re.escape(title) for title in section_titles) + ")"
    matches = list(re.finditer(pattern, text))
    sections = {}
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = match.group(0)
        content = text[start:end].strip()
        sections[title] = content
    return sections

def query_rag_context(query, top_k=3):
    """
    Truy vấn vector database để lấy top_k đoạn context liên quan nhất đến query.
    """
    embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.Client()
    collection = client.get_or_create_collection("rag_docs", embedding_function=embedding_function)
    results = collection.query(query_texts=[query], n_results=top_k)
    # Lấy các đoạn văn bản liên quan nhất
    docs = results["documents"][0] if "documents" in results else []
    if not docs:
        return "Không tìm thấy thông tin liên quan trong RAG.txt."
    return "\n".join(docs)

def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(url, headers=headers, data=json.dumps(data))
    if res.status_code == 200:
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Lỗi gọi API ({res.status_code}):\n{res.text}"

def answer_pdf_tai_trong(pdf_file: bytes):
    """
    Trích xuất thông tin về tải trọng.
    """
    import tempfile
    section_titles = [
        "Quy hoạch hệ thống giao thông",
        "Giao thông đối ngoại",
        "Giao thông đối nội"
    ]
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_file)
        tmp_path = tmp.name
    sections = extract_sections_by_titles(tmp_path, section_titles)
    if not sections:
        return "Không tìm thấy nội dung các mục yêu cầu."
    rag_context = query_rag_context("tải trọng xe chữa cháy theo TCVN 2737")
    prompt = f"""
Bạn là chuyên gia kiểm tra thuyết minh xây dựng về phòng cháy chữa cháy. Đây là tài liệu tham khảo:

{rag_context}

---
"""
    for title in section_titles:
        prompt += f"[{title}]\n{sections.get(title, '')}\n\n"
    prompt += "Kiểm tra xem trong dữ liệu trên có dữ liệu chính xác về tải trọng nền đường cho xe, bãi đỗ hay không. Nếu có số liệu về tải trọng nền đường cho xe, bãi đỗ hãy trích nguyên văn. Còn nếu không số liệu về tải trọng đó thì trả lời nguyên văn là Không có thông tin về tải trọng nền đường cho xe, bãi đỗ. Kết quả chỉ được dùng dấu chấm và dấu phẩy. Bạn phải xác định đúng từ khóa ở đây là tải trọng nền đường cho xe, bãi đỗ chứ không phải các từ khác."
    result = call_gemini(prompt)
    return result


def answer_pdf_luu_luong(pdf_file: bytes):
    """
    Trích xuất thông tin về lưu lượng nước.
    """
    import tempfile
    section_titles = [
        "Quy hoạch hệ thống cấp nước",
        "Dự báo nhu cầu dùng nước",
        "Hệ thống cấp nước chữa cháy"
    ]
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_file)
        tmp_path = tmp.name
    sections = extract_sections_by_titles(tmp_path, section_titles)
    if not sections:
        return "Không tìm thấy nội dung các mục yêu cầu."
    rag_context = query_rag_context("lưu lượng nước chữa cháy")
    prompt = f"""
Bạn là chuyên gia kiểm tra thuyết minh xây dựng về phòng cháy chữa cháy. Đây là tài liệu tham khảo:

{rag_context}

---
"""
    for title in section_titles:
        prompt += f"[{title}]\n{sections.get(title, '')}\n\n"
    prompt += "Kiểm tra xem có đề cập đến lưu lượng nước (nhu cầu nước sinh hoạt, nhu cầu nước chữa cháy, tổng nhu cầu nước/ngày) hay không.\nNếu có thông tin về lưu lượng nước hãy liệt kê số liệu cụ thể. Nếu không có thông tin thì cảnh báo không có."
    prompt += "Trình bày câu trả lời rõ ràng, không được thêm các dấu * hay -, chỉ dùng dấu . và dấu ,"
    result = call_gemini(prompt)
    return result

def rag_for_task12(pdf_file: bytes):
    """
    Trích xuất thông tin về dân số."""
    import tempfile
    section_titles = [
        "Phạm vi quy hoạch."
    ]
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_file)
        tmp_path = tmp.name
    sections = extract_sections_by_titles(tmp_path, section_titles)
    if not sections:
        return "Không tìm thấy nội dung các mục yêu cầu."
    rag_context = query_rag_context("dân số")
    prompt = f"""
Bạn là chuyên gia tìm thông tin về dân số trong thuyết minh xây dựng. Đây là tài liệu tham khảo:

{rag_context}

---
"""
    for title in section_titles:
        prompt += f"[{title}]\n{sections.get(title, '')}\n\n"
    prompt += "Kiểm tra xem có đề cập đến dân số hay không.\nNếu có thông tin về dân số hãy liệt kê số liệu cụ thể. Nếu không có thông tin thì cảnh báo không có."
    result = call_gemini(prompt)
    return result
