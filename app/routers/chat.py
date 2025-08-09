from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import List
import requests
import shutil
import sys
import os
import json
import asyncio
import os
import shutil
from typing import List
import sys
from pydantic import BaseModel 
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from setting.global_var import session_folders, UPLOAD_DIR, AGENT_API_KEY, MCP_URL, GEMINI_MODEL, TEMP_DIR, UPLOAD_DIR

router = APIRouter()

templates = Jinja2Templates(directory=TEMP_DIR)

# In-memory chat log for demonstration
chat_history = []


def choose_tool_llm(user_request: str):
    """
    Dùng Gemini để phân tích yêu cầu đầu vào để chọn tool phù hợp.
    """
    prompt = f"""
Bạn là AI Agent. Dưới đây là yêu cầu của người dùng: \"{user_request}\\\"

Chọn đúng 1 từ khoá sau để trả lời:
- task3: Nếu yêu cầu liên quan đến kiểm tra tải trọng nền đường cho xe, bãi đỗ trong file thuyết minh PDF.
- task11: Nếu yêu cầu liên quan đến kiểm tra yêu cầu về lưu lượng nước trong file thuyết minh PDF.
- task9: Nếu yêu cầu liên quan đến nhận diện trụ cứu hỏa và khoảng cách giữa các trụ cứu hỏa.
- task2: Nếu yêu cầu liên quan đến kiểm tra chiều rộng đường nội bộ hoặc bãi đỗ xe chữa cháy.
- task5: Nếu yêu cầu liên quan đến kiểm tra có thể hiện đoạn dốc hay không. 
- task6: Nếu yêu cầu liên quan đến đoạn tránh xe.
- task4: Nếu yêu cầu lien quan đến khoảng cách từ mép đường tới tường nhà hoặc công trình.
- task13: Nếu yêu cầu liên quan đến hệ thống thông tin liên lạc hoặc cung cấp điện.
- task1: Nếu yêu cầu liên quan đến khoảng cách phòng cháy giữa các tòa nhà.
- task12: Nếu yêu cầu liên quan đến số lượng đám cháy tính toán.
- all: Nếu yêu cầu là kiểm tra toàn bộ đồ án.

Ví dụ:
- \"Kiểm tra tải trọng nền đường cho xe, bãi đỗ trong file thuyết minh sau?\" => task3
- \"Kiểm tra thông tin về lưu lượng nước trong file thuyết minh sau?\" => task11
- \"Kiểm tra các trụ cứu hỏa và khoảng cách giữa chúng?\" => task9
- \"Kiểm tra chiều rộng đường nội bộ và bãi đỗ xe chữa cháy trong bản vẽ sau?\" => task2
- \"Kiểm tra đoạn dốc trong bản vẽ sau?\" => task5
- \"Kiểm tra đoạn tránh xe trong bản vẽ sau?\" => task6
- \"Kiểm tra khoảng cách từ mép đường tới tường nhà trong bản vẽ sau?\" => task4
- \"Kiểm tra hệ thống thông tin liên lạc hoặc cung cấp điện trong bản vẽ sau?\" => task13
- \"Kiểm tra khoảng cách phòng cháy giữa các tòa nhà trong bản vẽ sau?\" => task1
- \"Kiểm tra số lượng đám cháy tính toán trong bản vẽ sau?\" => task12
- \"Kiểm tra toàn bộ đồ án\" => all

Chỉ trả về duy nhất 1 từ khoá: task1, task2, task3, task4, task5, task6, task9, task11, task12, task13.
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/{GEMINI_MODEL}:generateContent?key={AGENT_API_KEY}"
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

async def process_file(session_id: str,message: str):

    tool = choose_tool_llm(message)

    session_dir = os.path.join(UPLOAD_DIR,f"session_{session_id}")

    try:
        if os.path.isdir(session_dir):
            print(session_dir)
    except Exception as e:          
        print(e)
        return {"response": f"Không có dữ liệu để kiểm tra {tool}."}
    
    # Các task còn lại chỉ cần truyền session_dir
    try:
        if tool in ["task1", "task2", "task3", "task4", "task5", "task6", "task9", "task11", "task12", "task13", "all"]:
            if not session_dir:
                return {"response": "Thiếu session_dir"}
            response = requests.post(f"{MCP_URL}/tools/run_{tool}", data={"session_dir": session_dir})
            if response.status_code == 200:
                return {"response": response.json()["result"]}
            return {"response": f"Không thể xử lý yêu cầu {tool}"}
        else:
            return {"response": f"Không thể xử lý yêu cầu kiêm tra toàn bộ đồ án"}
    except:
        return {"response": "Không nhận diện được yêu cầu, vui lòng nhập lại."}


@router.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    if not request.session.get("logged_in"):
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("chat.html", {
        "request": request,
        "chat_history": chat_history
    })

@router.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, message: str = Form(...)):
    if not request.session.get("logged_in"):
        return RedirectResponse(url="/login")

    session_id = request.session.get("session_id")

    try:
        
        response = await process_file(session_id,message)

        result = response["response"]
        # Nếu result là string json, phải parse về dict
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                pass  # Nếu không phải json thì thôi

        if isinstance(result, dict) and "html" in result:
            ai_reply = result["html"]
            # Nếu có id, có thể trả ra cho FE dùng zoom (hoặc bỏ nếu không cần)
            return JSONResponse(content={"user": message, "ai": ai_reply})
        else:
            ai_reply = result
            return JSONResponse(content={"user": message, "ai": ai_reply})
    except Exception as e:
        ai_reply = f"Error contacting agent: {e}"
        return JSONResponse(content={"user": message, "ai": ai_reply})

@router.post("/upload")
async def upload_folder(request: Request, files: List[UploadFile] = File(...)):
    session_id = request.session.get("session_id")
    session_dir = os.path.join(UPLOAD_DIR, f"session_{session_id}")
    input_dir = os.path.join(session_dir, f"input")
    process_dir = os.path.join(session_dir, f"process")
    output_dir = os.path.join(session_dir, f"output")

    if os.path.exists(session_dir):
        shutil.rmtree(session_dir)
        
    os.makedirs(session_dir, exist_ok=True)
    os.makedirs(input_dir,exist_ok=True)
    os.makedirs(process_dir,exist_ok=True)
    os.makedirs(output_dir,exist_ok=True)
    session_folders[session_id] = {"name": session_dir, "born_time": time.time()}
    saved_files = []

    try:
        form_files = []
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
            

    except Exception as e:
        result = f"Error contacting agent: {e}"
        return JSONResponse(content={"status": "uploaded", "file":  result})

    return JSONResponse(content={"status": "uploaded", "file": saved_files})

@router.post("/logout")
async def logout(request: Request):
    try:
        request.session.clear()
    except:
        pass

@router.get("/download")
async def download(request:Request):
    session_id = request.session.get("session_id")
    file_path = os.path.join(UPLOAD_DIR, f"session_{session_id}", "output", "Ket_qua_doi_chieu.doc")

    if os.path.exists(file_path):
        print("✅ File exists, returning it.")
        return FileResponse(
            path=file_path,
            filename="Ket_qua_doi_chieu.doc",
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    return {"error": "File not found"}