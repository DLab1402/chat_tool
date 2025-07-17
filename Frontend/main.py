import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Settings
from routers import login, chat, visual
from utils.global_var import STATIC_DIR, TEMP_DIR

def create_app():
    app = FastAPI()
    
    app.add_middleware(SessionMiddleware, secret_key=Settings.SECRET_KEY)
    
    # Static and templates
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.templates = Jinja2Templates(directory=TEMP_DIR)

    # Routers
    app.include_router(login.router)
    app.include_router(chat.router)
    app.include_router(visual.router)

    return app