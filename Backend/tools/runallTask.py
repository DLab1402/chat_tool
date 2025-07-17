# ==== IMPORTS ===
import uuid
import subprocess
import sys
import os
import tempfile
import base64
from fastapi import FastAPI, UploadFile, File, Form
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.global_var import TEMPLATE_PATH, AGENT_API_KEY,FORNTEND_IP, FRONTEND_PORT
from utils.output_collector import output_collector, llm_compare_func_gemini_task1, llm_compare_func_gemini_task3, llm_compare_func_gemini_task4, llm_compare_func_gemini_task5, llm_compare_func_gemini_task6, llm_compare_func_gemini_task9, llm_compare_func_gemini_task11, llm_compare_func_gemini_task12, llm_compare_func_gemini_task13

from tools.Task_1n12.runTask1n12 import runTask1n12
from tools.Task_3n11.runTask3 import runTask3
from tools.Task_4.runTask4 import runTask4
from tools.Task_3n11.runTask11 import runTask11
from tools.Task_13.runTask13 import runTask13
from tools.Task_9.runTask9 import runTask9
from tools.Task_6.runTask6 import runTask6

API_KEY = AGENT_API_KEY

def runallTask(session_dir):
    output_folder = os.path.join(session_dir, "output")

    OUTPUT_PATH = output_folder + "\Ket_qua_doi_chieu.doc"
   
    #Task 1
    task1n12 = runTask1n12(session_dir, single = False)
    if isinstance(task1n12,dict):
        task1_text = json.dumps(task1n12.get("Khoảng cách nhỏ nhất"), ensure_ascii=False, indent=2)
        task12_text = json.dumps(task1n12.get("Diện tích"), ensure_ascii=False, indent=2)
    else:
        task1_text = str(task1n12)
        task12_text = str(task1n12)
    
    output_collector(
        task1_text,
        TEMPLATE_PATH,
        OUTPUT_PATH,
        lambda res: llm_compare_func_gemini_task1(res, api_key=API_KEY),
        task="task1"
    )

    #Task 3
    task3_text = runTask3(session_dir)
    output_collector(
        task3_text,
        OUTPUT_PATH,
        OUTPUT_PATH,
        lambda res: llm_compare_func_gemini_task3(res, api_key=API_KEY),
        task="task3"
    )

    #Task 4
    task4 = runTask4(session_dir, single = False)
    if isinstance(task4,dict):
        task4_text = json.dumps(task4.get("Mép"), ensure_ascii=False, indent=2)
    else:
        task4_text = str(task4)

    output_collector(
        task4_text,
        OUTPUT_PATH,
        OUTPUT_PATH,
        lambda res: llm_compare_func_gemini_task4(res, api_key=API_KEY),
        task="task4"
    )

    #Task 6
    task6 = runTask6(session_dir, single = False)
    if isinstance(task6,dict):
        task6_text = json.dumps(task6.get("Đoạn tránh xe"), ensure_ascii=False, indent=2)
    else:
        task6_text = str(task6)

    output_collector(
        task6_text,
        OUTPUT_PATH,
        OUTPUT_PATH,
        lambda res: llm_compare_func_gemini_task6(res, api_key=API_KEY),
        task="task6"
    )

    #Task 9
    task9 = runTask9(session_dir, single = False)
    if isinstance(task9,dict):
        task9_text = json.dumps(task9.get("Trụ cứu hỏa"), ensure_ascii=False, indent=2)
    else:
        task9_text = str(task9)
    
    output_collector(
        task9_text,
        OUTPUT_PATH,
        OUTPUT_PATH,
        lambda res: llm_compare_func_gemini_task9(res, api_key=API_KEY),
        task="task9"
    )

    #Task 11
    task11_text = runTask11(session_dir)
    output_collector(
        task11_text,
        OUTPUT_PATH,
        OUTPUT_PATH,
        lambda res: llm_compare_func_gemini_task11(res, api_key=API_KEY),
        task="task11"
    )

    #Task 12
    output_collector(
        task12_text,
        OUTPUT_PATH,
        OUTPUT_PATH,
        lambda res: llm_compare_func_gemini_task12(res, api_key=API_KEY),
        task="task12"
    )

    #Task 13
    task13 = runTask13(session_dir, single = False)
    if isinstance(task13,dict):
        task13_text = json.dumps(task13.get("Tủ điện") + task13.get("Đường dây liên lạc"), ensure_ascii=False, indent=2)
    else:
        task13_text = str(task13)

    output_collector(
        task13_text,
        OUTPUT_PATH,
        OUTPUT_PATH,
        lambda res: llm_compare_func_gemini_task13(res, api_key=API_KEY),
        task="task13"
    )

    return "<a href='http://"+FORNTEND_IP+":"+str(FRONTEND_PORT)+"/download' download>Click: Kết quả đối chiếu.</a>"