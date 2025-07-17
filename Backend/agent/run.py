from ai_agent import create_agent
import uvicorn
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.global_var import BACKEND_IP,BACKTEND_PORT

agent = create_agent()

if __name__ == "__main__":
    uvicorn.run("run:agent", host=BACKEND_IP, port=BACKTEND_PORT, reload=True)