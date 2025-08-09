import os
import sys
import time
import shutil
import asyncio
from fastapi import FastAPI
import redis.asyncio as redis
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Settings
from routers import login, chat
from setting.global_var import STATIC_DIR,TEMP_DIR, UPLOAD_DIR, session_folders, TRIGGER_TIME, EXPIRE_TIME

async def clean_up_task():
    while True:
        try:
            print("Triggerd time")
            for session in session_folders:
                if os.path.isdir(session_folders[session]["name"]):
                    t = time.time() - session_folders[session]["born_time"]
                    print(t)
                    if t>= EXPIRE_TIME:
                        shutil.rmtree(session_folders[session]["name"])
                        del session_folders[session]
            await asyncio.sleep(TRIGGER_TIME)
        except Exception as e:
            print(f"Task error: {e}")

def create_app():
    for item in os.listdir(UPLOAD_DIR):
        item_path = os.path.join(UPLOAD_DIR, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)

    app = FastAPI()
    
    app.add_middleware(SessionMiddleware, secret_key=Settings.SECRET_KEY)
    
    # Static and templates
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.templates = Jinja2Templates(directory=TEMP_DIR)

    # Routers
    app.include_router(login.router)
    app.include_router(chat.router)

    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(clean_up_task())

    return app