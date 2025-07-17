from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List
import requests
import shutil
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.global_var import TEMP_DIR

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
        ai_reply = response.json()["response"]
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
        # ai_reply = response.json().get("response", "No response")
        ai_reply = response.json()["uploaded_files"]
        print(ai_reply)
    except Exception as e:
        ai_reply = f"Error contacting agent: {e}"
        return JSONResponse(content={"status": "uploaded", "file":  ai_reply})

    return JSONResponse(content={"status": "uploaded", "file": ai_reply})

@router.post("/cleanup")
async def cleanup_session(request: Request):
    session_id = request.session.get("session_id")
    print(session_id)
    if session_id:
        folder = session_folders.pop(session_id, None)
        if folder and os.path.exists(folder):
            shutil.rmtree(folder)
        request.session.clear()
    return {"status": "session cleaned"}