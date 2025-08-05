import os
import sys
import shutil
import asyncio
from fastapi import FastAPI
import redis.asyncio as redis
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Settings
from routers import login, chat, visual
from Frontend.utils.global_frontend import STATIC_DIR, REDIS, UPLOAD_DIR,TEMP_DIR

REDIS = redis.Redis(
    host="127.0.0.1",
    port=6379,  # <-- make sure this matches your Redis server
    decode_responses=True
)

async def redis_expired_listener():
    pubsub = REDIS.pubsub()
    await pubsub.psubscribe("__keyevent@0__:expired")
    async for message in pubsub.listen():
        if message['type'] == 'pmessage':
            expired_id = message['data']
            print(f"[Redis] Session expired: {expired_id}")
            folder_path = os.path.join(UPLOAD_DIR, "session_"+expired_id)
            shutil.rmtree(folder_path, ignore_errors=True)

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

    @app.on_event("startup")
    async def startup_event():
        await REDIS.config_set("notify-keyspace-events", "Ex")
        asyncio.create_task(redis_expired_listener())
    
    return app