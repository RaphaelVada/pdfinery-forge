from pydantic import BaseModel, Field
from datetime import date, datetime
from pathlib import Path
from typing import Optional, List
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)


class SavedAs(BaseModel):
    """Speicherhistorie eines Dokuments"""
    filename: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Document(BaseModel):
    """Hauptdokument mit UUID und Metadaten"""
    id: UUID = Field(default_factory=uuid4)
    original_filename: str = Field(..., description="Ursprünglicher Dateiname")
    saved_as: List[SavedAs] = Field(default_factory=list, description="Speicherhistorie")
    
    # Metadaten (anfangs leer)
    document_type: Optional[str] = None
    correspondent: Optional[str] = Field(None, description="Absender/Empfänger")
    customer_id: Optional[str] = Field(None, description="Kunden-/Vertragsnummer")
    document_number: Optional[str] = Field(None, description="Rechnungs-/Dokumentnummer")
    document_date: Optional[date] = Field(None, description="Dokumentdatum")
    
    def generate_filename(self) -> str:
        """Generiert standardisierten Dateinamen"""
        if not self.document_type or not self.correspondent:
            logger.debug(f"Document {self.id}: Unvollständige Metadaten, verwende Original-Dateinamen")
            return self.original_filename
        
        parts = []
        
        if self.document_date:
            parts.append(self.document_date.strftime("%Y%m%d"))
        
        parts.append(self.correspondent.replace(" ", "_"))
        
        if self.document_number:
            parts.append(self.document_number)
        
        if self.document_type:
            parts.append(self.document_type)
        
        filename = "_".join(parts) + ".pdf"
        logger.info(f"Document {self.id}: Generierter Dateiname: {filename}")
        return filename
    
    def add_saved_filename(self, filename: str) -> None:
        """Fügt einen Dateinamen zur Speicherhistorie hinzu"""
        self.saved_as.append(SavedAs(filename=filename))
        logger.info(f"Document {self.id}: Gespeichert als '{filename}'")
    
    @property
    def current_filename(self) -> str:
        """Gibt den aktuellsten Dateinamen zurück"""
        if self.saved_as:
            return self.saved_as[-1].filename
        return self.original_filename
    
    @property
    def is_saved(self) -> bool:
        """Gibt True zurück, wenn das Dokument bereits gespeichert wurde"""
        return len(self.saved_as) > 0