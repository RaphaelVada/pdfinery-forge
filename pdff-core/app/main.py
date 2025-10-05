from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from app.pages import pages_router , app_static
from app.api.v1 import api_v1_router
from app.dependencies import collection, storage
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logger.critical("Logging critical active")
logger.error("Logging error active")
logger.warning("Logging warning active")
logger.info("Logging info active")
logger.debug("Logging debug active")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: Dokumente laden"""
    print("LIFESPAN STARTUP")  # Simpler print statt logger
    logger.info("Starte Dokumenten-Ingestion...")
    
    # Erst neue PDFs einlesen
    storage.ingest_documents(collection)
    logger.info(f"{len(collection)} neue Dokumente ingested")
    
    # Dann existierende laden
    storage.load_documents(collection)
    logger.info(f"Insgesamt {len(collection)} Dokumente geladen")
    
    yield
    
    # Shutdown (optional cleanup)
    logger.info("Shutting down...")

app = FastAPI(
    title="PDFF Core",
    description="PDFinery Forge - Transform unstructured PDFs into standardized, metadata-rich files",
    version="0.1.0",
    lifespan=lifespan
)

# Include routers
app.include_router(pages_router)
app.include_router(api_v1_router)


#from fastapi.staticfiles import StaticFiles
#app_static = StaticFiles(directory="app/pages/static")
app.mount("/static", app_static, name="static")

@app.get("/health")
def health():
    """Root health check"""
    return {"status": "ok"}