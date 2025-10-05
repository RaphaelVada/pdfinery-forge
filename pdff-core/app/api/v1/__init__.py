from fastapi import APIRouter
from app.api.v1.documents import router as documents_router
# from app.api.v1.metadata import router as metadata_router

# Haupt-Router für v1
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(documents_router)
# api_v1_router.include_router(metadata_router)

__all__ = ["api_v1_router"]