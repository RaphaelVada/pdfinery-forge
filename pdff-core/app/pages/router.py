from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])

# Templates setup
templates = Jinja2Templates(directory="app/pages/templates")

# Statische API-URL (später aus Config)
API_BASE_URL = "http://localhost:8000/api/v1"


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing page for PDFinery Forge"""
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "api_url": API_BASE_URL
        }
    )


@router.get("/editor", response_class=HTMLResponse)
async def editor(request: Request, document_id: str):
    """PDF Metadata Editor"""
    return templates.TemplateResponse(
        "editor.html",
        {
            "request": request,
            "document_id": document_id,
            "api_url": API_BASE_URL
        }
    )