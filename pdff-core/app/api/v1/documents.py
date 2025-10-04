from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from uuid import UUID
import base64

from app.models import DocumentCollection
from app.services.local_storage_service import LocalStorageService
from app.dependencies import get_collection, get_storage

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents(collection: DocumentCollection = Depends(get_collection)):
    """Liste aller Dokument-IDs"""
    return {
        "count": len(collection),
        "document_ids": [str(doc.id) for doc in collection.all()]
    }


@router.get("/{document_id}")
def get_document_pdf(
    document_id: UUID,
    collection: DocumentCollection = Depends(get_collection),
    storage: LocalStorageService = Depends(get_storage)
):
    """Gibt PDF im Browser aus"""
    doc = collection.get(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        base64_pdf = storage.load_pdf_as_base64(doc)
        pdf_bytes = base64.b64decode(base64_pdf)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={doc.current_filename}"
            }
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="PDF file not found in archive")