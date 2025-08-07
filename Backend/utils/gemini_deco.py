import re

def gemini_to_chatbot_html(text: str) -> str:
    html_lines = []
    in_list = False

    lines = text.splitlines()

    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append('<br>')
            continue

        # Bullet point
        if stripped.startswith("* "):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = stripped[2:].strip()
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
            html_lines.append(f'<li>{content}</li>')
        else:
            # Close list if needed
            if in_list:
                html_lines.append('</ul>')
                in_list = False

            # Bold inline text
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", stripped)
            html_lines.append(f'<div>{content}</div>')

    # Final close list
    if in_list:
        html_lines.append('</ul>')

    return '\n'.join(html_lines)