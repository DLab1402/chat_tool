from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse

import uuid
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.user_db import user_list

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse("/login")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
        print(session_id)
    return request.app.templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in user_list:
        if user_list[username] == password:
            request.session["logged_in"] = True
            return RedirectResponse("/chat", status_code=302)
    return request.app.templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})