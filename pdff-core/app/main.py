from fastapi import FastAPI
from app.pages.router import router as pages_router
from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title="PDFF Core",
    description="PDFinery Forge - Transform unstructured PDFs into standardized, metadata-rich files",
    version="0.1.0"
)

# Include routers
app.include_router(pages_router)
app.include_router(api_v1_router, prefix="/api/v1", tags=["api-v1"])

@app.get("/health")
def health():
    """Root health check"""
    return {"status": "ok"}