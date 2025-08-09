import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")