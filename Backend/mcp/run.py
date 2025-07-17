from mcp_server import create_mcp
import uvicorn
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.global_var import MCP_IP, MCP_PORT

mcp = create_mcp()

if __name__ == "__main__":
    uvicorn.run("run:mcp", host=MCP_IP, port=MCP_PORT, reload=True)