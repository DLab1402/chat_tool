from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/visual", response_class=HTMLResponse)
async def visual_page(request: Request):
    if not request.session.get("logged_in"):
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("visual.html", {"request": request})
