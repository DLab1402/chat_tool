from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse,FileResponse
from fastapi.templating import Jinja2Templates
from typing import List
import requests
import shutil
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.global_frontend import TEMP_DIR, UPLOAD_DIR

router = APIRouter()

templates = Jinja2Templates(directory=TEMP_DIR)

# In-memory chat log for demonstration
chat_history = []

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
        response = requests.post("http://127.0.0.1:8001/agent", json={"session_id": session_id, "message": message})
        response.raise_for_status()
        result = response.json()["response"]
        # Nếu result là string json, phải parse về dict
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                pass  # Nếu không phải json thì thôi

        if isinstance(result, dict) and "html" in result:
            ai_reply = result["html"]
            # Nếu có id, có thể trả ra cho FE dùng zoom (hoặc bỏ nếu không cần)
            return JSONResponse(content={"user": message, "ai": ai_reply, "id": result.get("id")})
        else:
            ai_reply = result
            return JSONResponse(content={"user": message, "ai": ai_reply})
    except Exception as e:
        ai_reply = f"Error contacting agent: {e}"
        return JSONResponse(content={"user": message, "ai": ai_reply})

@router.post("/upload")
async def upload_folder(request: Request, files: List[UploadFile] = File(...)):
    session_id = request.session.get("session_id")
    try:
        form_files = []
        for file in files:
            content = await file.read()
            form_files.append(
                ('files', (file.filename, content, file.content_type))
            )
        # Add session_id as form data
        data = {'session_id': session_id}

        response = requests.post(
            url="http://127.0.0.1:8001/upload", 
            files=form_files,
            data=data
        )
        response.raise_for_status()
        ai_reply = response.json()["uploaded_files"]
        print(ai_reply)
    except Exception as e:
        ai_reply = f"Error contacting agent: {e}"
        return JSONResponse(content={"status": "uploaded", "file":  ai_reply})

    return JSONResponse(content={"status": "uploaded", "file": ai_reply})

@router.post("/logout")
async def logout(request: Request):
    try:
        request.session.clear()
    except:
        pass

@router.get("/download")
async def download(request:Request):
    session_id = request.session.get("session_id")
    print(session_id)
    response = requests.post(
            url=f"http://127.0.0.1:8001/download/{session_id}"
        )
    print(response)