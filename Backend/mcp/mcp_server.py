# ==== IMPORTS ===
import os
import sys
import base64
from fastapi import FastAPI, UploadFile, File, Form

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.output_collector import output_collector, llm_compare_func_gemini
from utils.global_var import AGENT_API_KEY
from tools.Task_1n12.runTask1n12 import runTask1n12
from tools.Task_3n11.runTask3 import runTask3
from tools.Task_3n11.runTask11 import runTask11
from tools.runallTask import runallTask
from tools.Task_2.runTask2 import runTask2
from tools.Task_4.runTask4 import runTask4
# from tools.Task_5.runTask5 import runTask5, OUTPUT_PATH as OUTPUT_PATH_5
from tools.Task_6.runTask6 import runTask6
from tools.Task_13.runTask13 import runTask13
from tools.Task_9.runTask9 import runTask9

# ==== CONFIGURATION ====
API_KEY = AGENT_API_KEY

# ==== APP INIT ====
from mcp.server.fastmcp import FastMCP

def create_mcp():
    mcp = FastMCP("BCONS_MCP")
    app = FastAPI()

    # ==== TOOL DEFINITIONS ====
    @mcp.tool()
    def run_task1_tool(session_dir: str):
        """Tool thực hiện Task 1: Tính khoảng cách ngắn nhất giữa các contour."""
        return runTask1n12(session_dir)

    @mcp.tool()
    def run_task2_tool(session_dir: str):
         """Tool thực hiện Task 2: chuyển đổi và xử lý ảnh, phát hiện bãi đỗ xe, ..."""
         return runTask2(session_dir)

    @mcp.tool()
    def run_task3_tool(session_dir: str):
        """Tool thực hiện Task 3: kiểm tra tải trọng nền đường cho xe, bãi đỗ."""
        return runTask3(session_dir)

    @mcp.tool()
    def run_task4_tool(session_dir: str):
        """Tool thực hiện Task 4: kiểm tra chiều rộng đường."""
        return runTask4(session_dir)

    # @mcp.tool()
    # def run_task5_tool(session_dir: str):
    #     """Tool thực hiện Task 5: phân tích độ dốc, phát hiện box, ..."""
    #     return runTask5(session_dir)

    @mcp.tool()
    def run_task6_tool(session_dir: str):
        """Tool thực hiện Task 6: kiểm tra đoạn tránh xe."""
        return runTask6(session_dir)
    
    @mcp.tool()
    def run_task9_tool(session_dir: str):
        """Tool thực hiện Task 9: nhận diện trụ cứu hỏa và khoảng cách giữa các trụ cứu hỏa."""
        return runTask9(session_dir)
    
    @mcp.tool()
    def run_task11_tool(session_dir: str):
        """Tool thực hiện Task 11: kiểm tra lưu lượng nước chữa cháy."""
        return runTask11(session_dir)

    @mcp.tool()
    def run_task12_tool(session_dir: str):
        """Tool thực hiện Task 12: Tính diện tích các contour."""
        return runTask1n12(session_dir)

    @mcp.tool()
    def run_task13_tool(session_dir: str):
        """Tool thực hiện Task 13: kiểm tra hệ thống thông tin liên lạc hoặc cung cấp điện."""
        return runTask13(session_dir)
    
    @mcp.tool()
    def run_all_tool(session_dir: str):
        """Tool thực hiện all"""
        return runallTask(session_dir)

    # ==== API ENDPOINTS ====
    @app.post("/tools/run_task1")
    async def run_task1_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask1n12(session_dir)
        return {"result": result}

    @app.post("/tools/run_task2")
    async def run_task2_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask2(session_dir)
        return {"result": result}

    @app.post("/tools/run_task3")
    async def run_task3_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask3(session_dir)
        print(result)
        return {"result": result}

    @app.post("/tools/run_task4")
    async def run_task4_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask4(session_dir)
        import json
        result_text = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else str(result)
        return {"result": result_text}

    # @app.post("/tools/run_task5")
    # async def run_task5_api(session_dir: str = Form(...)):
    #     result = runTask5(session_dir)
    #     import json
    #     result_text = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else str(result)
    #     return {"result": result_text, "word_file": OUTPUT_PATH_5}

    @app.post("/tools/run_task6")
    async def run_task6_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask6(session_dir)
        import json
        result_text = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else str(result)
        print(result_text)
        return {"result": result_text}

    @app.post("/tools/run_task9")
    async def run_task9_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask9(session_dir)
        import json
        result_text = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else str(result)
        print(result_text)
        return {"result": result_text}

    @app.post("/tools/run_task11")
    async def run_task11_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask11(session_dir)
        return {"result": result}

    @app.post("/tools/run_task12")
    async def run_task12_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask1n12(session_dir)
        return {"result": result}

    @app.post("/tools/run_task13")
    async def run_task13_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask13(session_dir)
        import json
        result_text = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else str(result)
        print(result_text)
        return {"result": result_text}
    
    @app.post("/tools/run_all")
    async def run_all_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runallTask(session_dir)
        return {"result": result}
        
    return app