from main import create_app
import uvicorn
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.global_var import FORNTEND_IP,FRONTEND_PORT

app = create_app()

if __name__ == "__main__":
    uvicorn.run("run:app", host=FORNTEND_IP, port=FRONTEND_PORT, reload=True)