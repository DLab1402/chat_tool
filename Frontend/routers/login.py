from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import uuid
import sys
import os

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
    if username == "admin" and password == "1234":
        request.session["logged_in"] = True
        return RedirectResponse("/chat", status_code=302)
    return request.app.templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)