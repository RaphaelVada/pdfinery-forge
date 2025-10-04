from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])

# Templates setup
templates = Jinja2Templates(directory="app/pages/templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing page for PDFinery Forge"""
    return templates.TemplateResponse("index.html", {"request": request})