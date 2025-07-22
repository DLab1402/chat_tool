import cv2
import base64
import numpy as np
from typing import Dict
from io import BytesIO
from PIL import Image

def generate_zoomable_image_html(base64_img: str) -> str:
    return f'''
    <div>
    <style>
        .container {{
            width: 90vw;
            height: 90vh;
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f0f0f0;
            position: relative;
            cursor: grab;
        }}

        .image-wrapper {{
            position: absolute;
            top: 0;
            left: 0;
            transform-origin: top left;
            transition: transform 0.1s ease-out;
        }}

        .reset-button {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #888;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 14px;
            border-radius: 5px;
            z-index: 10;
        }}

        img {{
            display: block;
            max-width: none;
            max-height: none;
            user-select: none;
            -webkit-user-drag: none;
        }}
    </style>

    <div class="container"   script >
        <div class="reset-button" onclick="resetZoom()">Reset</div>
        <div class="image-wrapper" id="img-wrapper">
            <img id="zoom-img" src="{base64_img}" alt="Zoomable Image">
        </div>
    </div>

    <script>

    </script>
    </div>
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

    for i, (key, value) in enumerate(items):
        if isinstance(value, np.ndarray):  # Last key is image
            html_lines.append(f'<div><strong>IMAGE:</strong></div>')
            img_b64 = cv2_image_to_base64(value)
            html_lines.append(f'<div><img src="{img_b64}" alt="{key}" style="max-width: 100%; height: auto;"></div>')
            # html_lines.append(generate_zoomable_image_html(img_b64))
        else:
            if isinstance(value,list):
                html_lines.append(f'<div><strong>{key}:</strong></div>')
                for ite in value:
                    html_lines.append(f'<div>- {ite}.</div>')
            elif isinstance(value,str):
                html_lines.append(f'<div><strong>{key}</strong>: {value}.</div>')

    return '\n'.join(html_lines)