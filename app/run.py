import uvicorn
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from setting.global_var import APP_IP, APP_PORT
from main import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("run:app", host=APP_IP, 
                port=APP_PORT,
                reload=True)