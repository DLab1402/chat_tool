import os
import sys
import uuid
from multiprocessing import Process
from fastapi import FastAPI, Form

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ===== APP INIT =====
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

    @app.post("/tasks/start")
    async def start_task(session_dir: str = Form(...), task_name: str = Form(...)):
        if task_name not in task_map:
            return {"error": f"Invalid task name: {task_name}"}

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
    
    return app