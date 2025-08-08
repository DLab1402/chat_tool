# ==== IMPORTS ====
import requests
import json
import io
import base64
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from typing import Optional

import uvicorn
import os
import shutil
from typing import List
import sys
from pydantic import BaseModel  

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.global_backend import session_folders, UPLOAD_DIR, AGENT_API_KEY, MCP_IP, MCP_PORT

# ==== CONFIGURATION ====
MCP_SERVER_URL = "http://"+MCP_IP+":"+str(MCP_PORT)
GEMINI_API_KEY = AGENT_API_KEY
GEMINI_MODEL = "models/gemini-1.5-pro-latest"

# Thêm biến lưu task_id cuối cùng cho từng session
last_task_ids = {}

def create_agent():
    # ==== APP INIT ====
    app = FastAPI()

    # ==== TOOL CHOOSER ====
    def choose_tool_llm(user_request: str):
        """
        Dùng Gemini để phân tích yêu cầu đầu vào để chọn tool phù hợp.
        """
        prompt = f"""
    Bạn là AI Agent. Dưới đây là yêu cầu của người dùng: \"{user_request}\\\"

    Chọn đúng 1 từ khoá sau để trả lời:
    - task1: Nếu yêu cầu liên quan đến khoảng cách phòng cháy giữa các tòa nhà.
    - task2: Nếu yêu cầu liên quan đến kiểm tra chiều rộng đường nội bộ hoặc bãi đỗ xe chữa cháy.
<<<<<<< HEAD
    - task3: Nếu yêu cầu liên quan đến kiểm tra tải trọng nền đường cho xe, bãi đỗ trong file thuyết minh PDF.
    - task4: Nếu yêu cầu lien quan đến khoảng cách từ mép đường tới tường nhà hoặc công trình.
    - task5: Nếu yêu cầu liên quan đến kiểm tra có thể hiện đoạn dốc hay không.
=======
    - task5: Nếu yêu cầu liên quan đến kiểm tra có thể hiện đoạn dốc hay không. 
>>>>>>> 12b9bf1f42dfabaed6476ad55559541f2254a92a
    - task6: Nếu yêu cầu liên quan đến đoạn tránh xe.
    - task9: Nếu yêu cầu liên quan đến nhận diện trụ cứu hỏa và khoảng cách giữa các trụ cứu hỏa.
    - task11: Nếu yêu cầu liên quan đến kiểm tra yêu cầu về lưu lượng nước trong file thuyết minh PDF.
    - task12: Nếu yêu cầu liên quan đến số lượng đám cháy tính toán.
    - task13: Nếu yêu cầu liên quan đến hệ thống thông tin liên lạc hoặc cung cấp điện.
    - all: Nếu yêu cầu là kiểm tra toàn bộ.

    Ví dụ:
    - \"Kiểm tra khoảng cách phòng cháy giữa các tòa nhà\" => task1
    - \"Kiểm tra chiều rộng đường nội bộ và bãi đỗ xe chữa cháy\" => task2
    - \"Kiểm tra tải trọng nền đường cho xe, bãi đỗ\" => task3
    - \"Kiểm tra khoảng cách từ mép đường tới tường nhà\" => task4
    - \"Kiểm tra đoạn dốc\" => task5
    - \"Kiểm tra đoạn tránh xe\" => task6
    - \"Kiểm tra các trụ cứu hỏa và khoảng cách giữa chúng\" => task9
    - \"Kiểm tra thông tin về lưu lượng nước\" => task11
    - \"Kiểm tra số lượng đám cháy tính toán\" => task12
    - \"Kiểm tra hệ thống thông tin liên lạc hoặc cung cấp điện\" => task13
    - \"Kiểm tra toàn bộ\" => all

    Chỉ trả về duy nhất 1 từ khoá: task1, task2, task3, task4, task5, task6, task9, task11, task12, task13.
    """
        url = f"https://generativelanguage.googleapis.com/v1beta/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(url, headers=headers, data=json.dumps(data))
        if res.status_code == 200:
            result = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            print("Gemini trả về:", result)
            return result
        else:
            print("Gemini lỗi:", res.text)
            return "unknown"

    class Message(BaseModel):
        session_id: str
        message: str

    # ==== MAIN PROCESS ENDPOINT ====
    @app.post("/agent/")
    async def process_file(user_request: Message):
        message = user_request.message.strip().lower()
        session_id = user_request.session_id
        session_dir = f"{UPLOAD_DIR}\\session_{session_id}"

        # Xử lý lệnh STOP đơn giản
        if message in ["stop", "dừng", "huy", "cancel"]:
            task_id = last_task_ids.get(session_id)
            if not task_id:
                return {"response": "Không có tác vụ nào để dừng."}
            try:
                response = requests.post(f"{MCP_SERVER_URL}/tasks/stop/{task_id}")
                if response.status_code == 200:
                    return {"response": f"Đã dừng."}
                return {"response": f"Không thể dừng task."}
            except Exception as e:
                return {"response": f"Lỗi khi dừng: {e}"}

        # Nếu không phải STOP, chạy logic chọn tool và start task
        tool = choose_tool_llm(user_request.message)

        if not os.path.isdir(session_dir):
            return {"response": f"Không có dữ liệu để kiểm tra {tool}."}

        try:
            if tool in ["task1", "task2", "task3", "task4", "task5", "task6", "task9", "task11", "task12", "task13", "all"]:
                response = requests.post(f"{MCP_SERVER_URL}/tasks/start", data={"session_dir": session_dir, "task_name": tool})
                if response.status_code == 200:
                    data = response.json()
                    task_id = data.get("task_id")
                    last_task_ids[session_id] = task_id  # Lưu task_id cuối cùng
                    return {
                        "response": f"Đang chạy {tool}. Gõ 'stop' để dừng.",
                        "task_id": task_id,
                        "session_id": session_id
                    }
            else:
                return {"response": f"Không nhận diện được yêu cầu."}
        except Exception as e:
            return {"response": f"Lỗi: {e}"}
        
    # ==== API: STOP TASK ====
    @app.post("/agent/stop")
    async def stop_task(task_id: str = Form(...)):
        try:
            response = requests.post(f"{MCP_SERVER_URL}/tasks/stop/{task_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    # ==== API: CHECK STATUS ====
    @app.get("/agent/status/{task_id}")
    async def task_status(task_id: str):
        try:
            response = requests.get(f"{MCP_SERVER_URL}/tasks/status/{task_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    @app.post("/upload")
    async def upload_folder(
        session_id: str = Form(...),
        files: List[UploadFile] = File(...)
    ):

        session_dir = os.path.join(UPLOAD_DIR, f"session_{session_id}")
        input_dir = os.path.join(session_dir, f"input")
        process_dir = os.path.join(session_dir, f"process")
        output_dir = os.path.join(session_dir, f"output")
            
        #Clear the previous data
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
            
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(input_dir,exist_ok=True)
        os.makedirs(process_dir,exist_ok=True)
        os.makedirs(output_dir,exist_ok=True)
        session_folders[session_id] = session_dir
        print(session_folders)
        saved_files = []

        for file in files:
            filename = file.filename
            clean_name = os.path.basename(filename)
            ext = file.filename.split(".")[-1].lower()
            if (ext == "pdf") or (ext in ["dwg", "dxf"] and clean_name.startswith("QH")):
                save_path = os.path.join(input_dir, clean_name)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                content = await file.read()
                with open(save_path, "wb") as f:
                    f.write(content)
                    print(clean_name)

                saved_files.append(clean_name)
                    
        return {
            "session_id": session_id,
            "uploaded_files": saved_files
        }

    @app.post("/download/{session_id}")
    async def download_result(session_id: str):
        file_path = os.path.join(UPLOAD_DIR, session_id, "output", "Ket_qua_doi_chieu.doc")
        print(session_id)
        print("File path:", file_path)

        if os.path.exists(r"D:\bcons_app\bcons_app\Backend\utils\Bảng đối chiếu quy hoạch.docx"):
            print("✅ File exists, returning it.")
            return FileResponse(
                path=r"D:\bcons_app\bcons_app\Backend\utils\Bảng đối chiếu quy hoạch.docx",
                filename="Ket_qua_doi_chieu.doc",
                media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        print("❌ File not found")
        return {"error": "File not found"}
    
    return app