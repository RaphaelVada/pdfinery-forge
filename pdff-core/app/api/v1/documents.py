from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from uuid import UUID
import base64
from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.models import DocumentCollection
from app.services.local_storage_service import LocalStorageService
from app.dependencies import get_collection, get_storage

router = APIRouter(prefix="/documents", tags=["documents"])


# Response Models
class MetadataResponse(BaseModel):
    """Metadaten-Response für Frontend"""
    document_type: Optional[str] = None
    correspondent: Optional[str] = None
    customer_id: Optional[str] = None
    document_number: Optional[str] = None
    document_date: Optional[date] = None


class DocumentResponse(BaseModel):
    """Vollständige Dokument-Response"""
    id: UUID
    original_filename: str
    current_filename: str
    is_saved: bool
    metadata: MetadataResponse


class MetadataUpdateRequest(BaseModel):
    """Request für Metadaten-Update"""
    document_type: Optional[str] = None
    correspondent: Optional[str] = None
    customer_id: Optional[str] = None
    document_number: Optional[str] = None
    document_date: Optional[date] = None


class SaveResponse(BaseModel):
    """Response nach Speicherung"""
    id: UUID
    generated_filename: str
    saved_to_output: bool
    output_path: str


@router.get("")
def list_documents(collection: DocumentCollection = Depends(get_collection)):
    """Liste aller Dokument-IDs"""
    return {
        "count": len(collection),
        "document_ids": [str(doc.id) for doc in collection.all()]
    }


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_metadata(
    document_id: UUID,
    collection: DocumentCollection = Depends(get_collection)
):
    """Metadaten eines Dokuments abrufen"""
    doc = collection.get(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=doc.id,
        original_filename=doc.original_filename,
        current_filename=doc.current_filename,
        is_saved=doc.is_saved,
        metadata=MetadataResponse(
            document_type=doc.document_type,
            correspondent=doc.correspondent,
            customer_id=doc.customer_id,
            document_number=doc.document_number,
            document_date=doc.document_date
        )
    )


@router.get("/{document_id}/pdf")
def get_document_pdf(
    document_id: UUID,
    collection: DocumentCollection = Depends(get_collection),
    storage: LocalStorageService = Depends(get_storage)
):
    """PDF-Datei im Browser anzeigen"""
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


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document_metadata(
    document_id: UUID,
    metadata: MetadataUpdateRequest,
    collection: DocumentCollection = Depends(get_collection),
    storage: LocalStorageService = Depends(get_storage)
):
    """Metadaten aktualisieren (speichert nur, generiert noch keine Datei)"""
    doc = collection.get(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Partial update der Metadaten
    update_data = metadata.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doc, field, value)
    
    # Metadaten im Storage aktualisieren
    storage.update_metadata(doc)
    
    return DocumentResponse(
        id=doc.id,
        original_filename=doc.original_filename,
        current_filename=doc.current_filename,
        is_saved=doc.is_saved,
        metadata=MetadataResponse(
            document_type=doc.document_type,
            correspondent=doc.correspondent,
            customer_id=doc.customer_id,
            document_number=doc.document_number,
            document_date=doc.document_date
        )
    )


@router.post("/{document_id}/save", response_model=SaveResponse)
def save_document_to_output(
    document_id: UUID,
    collection: DocumentCollection = Depends(get_collection),
    storage: LocalStorageService = Depends(get_storage)
):
    """Generiert Dateinamen und speichert PDF nach /data/out"""
    doc = collection.get(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Validierung: Mindestens document_type und correspondent müssen vorhanden sein
    if not doc.document_type or not doc.correspondent:
        raise HTTPException(
            status_code=400, 
            detail="Incomplete metadata: document_type and correspondent required"
        )
    
    try:
        output_path = storage.save_to_output(doc)
        
        return SaveResponse(
            id=doc.id,
            generated_filename=doc.current_filename,
            saved_to_output=True,
            output_path=str(output_path)
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")


@router.post("/{document_id}/preview-filename")
def preview_filename(
    document_id: UUID,
    metadata: MetadataUpdateRequest,
    collection: DocumentCollection = Depends(get_collection)
):
    """Preview des generierten Dateinamens ohne zu speichern - Zero-Copy"""
    doc = collection.get(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    from app.models.document import Document
    
    # Direkte Filename-Generierung ohne Object-Instanz
    preview_filename = Document.build_filename(
        document_type=metadata.document_type or doc.document_type,
        correspondent=metadata.correspondent or doc.correspondent,
        customer_id=metadata.customer_id or doc.customer_id,
        document_number=metadata.document_number or doc.document_number,
        document_date=metadata.document_date or doc.document_date,
        fallback_filename=doc.original_filename
    )
    
    is_complete = bool(
        (metadata.document_type or doc.document_type) and 
        (metadata.correspondent or doc.correspondent)
    )
    
    return {
        "preview_filename": preview_filename,
        "is_complete": is_complete
    }


class NavigationDocumentInfo(BaseModel):
    """Minimal-Info für Navigation"""
    id: UUID
    original_filename: str


class NavigationResponse(BaseModel):
    """Navigation zu vorherigem/nächstem Dokument"""
    current: NavigationDocumentInfo
    next: Optional[NavigationDocumentInfo] = None
    previous: Optional[NavigationDocumentInfo] = None
    total_unprocessed: int
    current_position: int


@router.get("/{document_id}/navigation", response_model=NavigationResponse)
def get_navigation(
    document_id: UUID,
    filter: str = "unprocessed",
    collection: DocumentCollection = Depends(get_collection)
):
    """
    Navigiere zu vorherigem/nächstem Dokument.
    Filter: 
    - 'unprocessed': Dokumente ohne vollständige Metadaten (kein document_type oder correspondent)
    - 'unsaved': Dokumente die noch nie gespeichert wurden
    - 'all': Alle Dokumente
    
    WICHTIG: Das aktuelle Dokument ist IMMER in der Liste, auch wenn es Filter-Kriterien nicht erfüllt.
    """
    current_doc = collection.get(document_id)
    
    if not current_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Alle Dokumente holen und filtern
    all_docs = collection.all()
    
    if filter == "unprocessed":
        # Dokumente ohne vollständige Metadaten
        filtered_docs = [
            doc for doc in all_docs 
            if not doc.document_type or not doc.correspondent
        ]
    elif filter == "unsaved":
        # Nur noch nie gespeicherte Dokumente
        filtered_docs = [doc for doc in all_docs if not doc.is_saved]
    else:
        filtered_docs = all_docs
    
    # WICHTIG: Aktuelles Dokument MUSS immer in der Liste sein
    if current_doc not in filtered_docs:
        filtered_docs.append(current_doc)
    
    # Sortieren nach original_filename für konsistente Reihenfolge
    filtered_docs.sort(key=lambda d: d.original_filename)
    
    # Current Position finden (sollte jetzt IMMER funktionieren)
    current_index = next(i for i, doc in enumerate(filtered_docs) if doc.id == document_id)
    
    # Previous & Next ermitteln
    previous_doc = filtered_docs[current_index - 1] if current_index > 0 else None
    next_doc = filtered_docs[current_index + 1] if current_index < len(filtered_docs) - 1 else None
    
    return NavigationResponse(
        current=NavigationDocumentInfo(
            id=current_doc.id,
            original_filename=current_doc.original_filename
        ),
        next=NavigationDocumentInfo(
            id=next_doc.id,
            original_filename=next_doc.original_filename
        ) if next_doc else None,
        previous=NavigationDocumentInfo(
            id=previous_doc.id,
            original_filename=previous_doc.original_filename
        ) if previous_doc else None,
        total_unprocessed=len(filtered_docs),
        current_position=current_index + 1  # 1-based für User
    )