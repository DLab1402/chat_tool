import os
import sys
<<<<<<< HEAD
import uuid
from multiprocessing import Process
from fastapi import FastAPI, Form

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ===== APP INIT =====
=======
import base64
import json
from fastapi import FastAPI, UploadFile, File, Form

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.output_collector import output_collector, llm_compare_func_gemini
from utils.global_backend import AGENT_API_KEY
from tools.Task_1n12.runTask1n12 import runTask1n12
from tools.Task_3n11.runTask3 import runTask3
from tools.Task_3n11.runTask11 import runTask11
from tools.runallTask import runallTask
from tools.Task_2.runTask2 import runTask2
from tools.Task_4.runTask4 import runTask4
from tools.Task_5.runTask5 import runTask5 
from tools.Task_6.runTask6 import runTask6
from tools.Task_13.runTask13 import runTask13
from tools.Task_9.runTask9 import runTask9

# ==== CONFIGURATION ====
API_KEY = AGENT_API_KEY

# ==== APP INIT ====
from mcp.server.fastmcp import FastMCP

>>>>>>> 12b9bf1f42dfabaed6476ad55559541f2254a92a
def create_mcp():
    app = FastAPI()

    # ===== TASK MAPPING =====
    from tools.Task_1n12.runTask1n12 import runTask1n12
    from tools.Task_3n11.runTask3 import runTask3
    from tools.Task_3n11.runTask11 import runTask11
    from tools.runallTask import runallTask
    from tools.Task_2.runTask2 import runTask2
    from tools.Task_4.runTask4 import runTask4
    from tools.Task_5.runTask5 import runTask5
    from tools.Task_6.runTask6 import runTask6
    from tools.Task_13.runTask13 import runTask13
    from tools.Task_9.runTask9 import runTask9

    task_map = {
        "task1": runTask1n12,
        "task2": runTask2,
        "task3": runTask3,
        "task4": runTask4,
        "task5": runTask5,
        "task6": runTask6,
        "task9": runTask9,
        "task11": runTask11,
        "task12": runTask1n12,  
        "task13": runTask13,
        "all": runallTask,
    }

    processes = {}

    # Hàm chạy task trong process riêng biệt
    def run_in_process(task_func, task_name, session_dir):
        task_func(session_dir)  

<<<<<<< HEAD
    @app.post("/tasks/start")
    async def start_task(session_dir: str = Form(...), task_name: str = Form(...)):
        if task_name not in task_map:
            return {"error": f"Invalid task name: {task_name}"}
=======
    @mcp.tool()
    def run_task5_tool(session_dir: str):
        """Tool thực hiện Task 5: phân tích độ dốc, phát hiện box, ..."""
        return runTask5(session_dir)
>>>>>>> 12b9bf1f42dfabaed6476ad55559541f2254a92a

        task_func = task_map[task_name]
        task_id = str(uuid.uuid4())
        p = Process(target=run_in_process, args=(task_func, task_name, session_dir))
        p.start()
        processes[task_id] = p

        return {
            "task_id": task_id,
            "task_name": task_name,
            "status": "started"
        }

    @app.post("/tasks/stop/{task_id}")
    async def stop_task(task_id: str):
        p = processes.get(task_id)
        if not p:
            return {"error": "Task not found"}
        if p.is_alive():
            p.terminate()
            p.join()
            return {"status": "terminated", "task_id": task_id}
        return {"status": "already finished", "task_id": task_id}

    @app.get("/tasks/status/{task_id}")
    async def task_status(task_id: str):
        p = processes.get(task_id)
        if not p:
            return {"error": "Task not found"}
        return {
            "task_id": task_id,
            "alive": p.is_alive()
        }
    
<<<<<<< HEAD
=======
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
        if isinstance(result, dict):
            return {"result": result}
        else:
            return {"result": result}

    @app.post("/tools/run_task5")
    async def run_task5_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask5(session_dir)
        if isinstance(result, dict):
            return {"result": result}
        else:
            return {"result": result}

    @app.post("/tools/run_task6")
    async def run_task6_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask6(session_dir)
        if isinstance(result, dict):
            return {"result": result}
        else:
            return {"result": result}

    @app.post("/tools/run_task9")
    async def run_task9_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runTask9(session_dir)
        if isinstance(result, dict):
            return {"result": result}
        else:
            return {"result": result}

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
        if isinstance(result, dict):
            return {"result": result}
        else:
            return {"result": result}
    
    @app.post("/tools/run_all")
    async def run_all_api(session_dir: str = Form(...)):
        print("==> Received session_dir:", session_dir)
        result = runallTask(session_dir)
        return {"result": result}
        
>>>>>>> 12b9bf1f42dfabaed6476ad55559541f2254a92a
    return app