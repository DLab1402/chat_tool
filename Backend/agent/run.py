from ai_agent import create_agent
import uvicorn
import shutil
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.global_backend import BACKEND_IP,BACKTEND_PORT,UPLOAD_DIR

for item in os.listdir(UPLOAD_DIR):
    item_path = os.path.join(UPLOAD_DIR, item)
    if os.path.isdir(item_path):
        shutil.rmtree(item_path)

agent = create_agent()

if __name__ == "__main__":
    uvicorn.run("run:agent", host=BACKEND_IP, port=BACKTEND_PORT, reload=True)