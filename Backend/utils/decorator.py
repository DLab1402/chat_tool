import cv2
import base64
import numpy as np
from typing import Dict
from io import BytesIO
from PIL import Image
import time

def generate_zoomable_image_html(base64_img: str) -> str:
    return f'''

    '''

def cv2_image_to_base64(img: np.ndarray) -> str:
    # Convert OpenCV BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    
    # Encode as PNG
    buffer = BytesIO()
    pil_img.save(buffer, format="PNG")
    base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    return f"data:image/png;base64,{base64_img}"

def dict_to_chat_html_with_cv2_image(data: Dict[str, any]) -> str:
    html_lines = []
    items = list(data.items())
    timestamp = int(time.time())
    for i, (key, value) in enumerate(items):
        if isinstance(value, np.ndarray):  # Last key is image
            html_lines.append(f'<div><strong>IMAGE:</strong></div>')
            img_b64 = cv2_image_to_base64(value)
            html_lines.append(f'''<div class = "image_frame" id = "{timestamp}">
                              <div class = "reset-button" onclick="resetZoom("{timestamp}")">Reset</div>
                              <div class = "image_wrapper" id = "{timestamp}1"><img src="{img_b64}" alt="{key}" style="max-width: 100%; height: auto;"></div>
                              </div>''')
                                #   <script>setupZoomPan("{timestamp}", "{timestamp}1");</script>''')
                            #   <div class="reset-button" onclick="resetZoom({str(timestamp)})">Reset</div>
        else:
            if isinstance(value,list):
                html_lines.append(f'<div><strong>{key}:</strong></div>')
                for ite in value:
                    html_lines.append(f'<div>- {ite}.</div>')
            elif isinstance(value,str):
                html_lines.append(f'<div><strong>{key}</strong>: {value}.</div>')

    return {"html":'\n'.join(html_lines),"id":timestamp}