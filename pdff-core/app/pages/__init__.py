from fastapi import APIRouter
from app.pages.router import router as template_router
from fastapi.staticfiles import StaticFiles

pages_router = APIRouter()
pages_router.include_router(template_router)
app_static = StaticFiles(directory="app/pages/static")

__all__ = ["pages_router", "app_static"]