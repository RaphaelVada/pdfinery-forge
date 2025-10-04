from typing import Dict, List, Optional
from uuid import UUID
import logging
from app.models.document import Document

logger = logging.getLogger(__name__)


class DocumentCollection:
    """Verwaltung einer Menge von Documents mit ID-basiertem Zugriff"""
    
    def __init__(self):
        self._documents: Dict[UUID, Document] = {}
    
    def add(self, document: Document) -> None:
        """Fügt ein Document zur Collection hinzu. Wirft ValueError bei doppelter ID."""
        if document.id in self._documents:
            raise ValueError(f"Document mit ID {document.id} existiert bereits in der Collection")
        self._documents[document.id] = document
        logger.debug(f"Document {document.id} zur Collection hinzugefügt")
    
    def get(self, document_id: UUID) -> Optional[Document]:
        """Holt ein Document per ID"""
        return self._documents.get(document_id)
    
    def remove(self, document_id: UUID) -> bool:
        """Entfernt ein Document aus der Collection"""
        if document_id in self._documents:
            del self._documents[document_id]
            logger.debug(f"Document {document_id} aus Collection entfernt")
            return True
        return False
    
    def all(self) -> List[Document]:
        """Gibt alle Documents als Liste zurück"""
        return list(self._documents.values())
    
    def __len__(self) -> int:
        """Anzahl der Documents in der Collection"""
        return len(self._documents)
    
    def __contains__(self, document_id: UUID) -> bool:
        """Prüft ob Document-ID in Collection vorhanden"""
        return document_id in self._documents