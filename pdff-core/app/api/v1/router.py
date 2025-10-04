from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    """API Health Check"""
    return {"status": "healthy", "version": "v1"}

# Später: Include endpoints
# from .endpoints import pdf, metadata
# router.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
# router.include_router(metadata.router, prefix="/metadata", tags=["metadata"])