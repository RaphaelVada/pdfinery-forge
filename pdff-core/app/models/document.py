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
    
    @staticmethod
    def build_filename(
        document_type: Optional[str],
        correspondent: Optional[str],
        customer_id: Optional[str] = None,
        document_number: Optional[str] = None,
        document_date: Optional[date] = None,
        fallback_filename: str = "document.pdf"
    ) -> str:
        """
        Statische Methode zur Filename-Generierung ohne Object-Instanz.
        Perfekt für Previews ohne Memory-Overhead.
        """
        if not document_type or not correspondent:
            return fallback_filename
        
        parts = []
        
        if document_date:
            parts.append(document_date.strftime("%Y%m%d"))
        
        parts.append(correspondent.replace(" ", "_"))
        
        if document_number:
            parts.append(document_number)
        
        if document_type:
            parts.append(document_type)
        
        filename = "_".join(parts) + ".pdf"
        return filename
    
    @property
    def generated_filename(self) -> str:
        """Computed property für generierten Filename"""
        return self.build_filename(
            document_type=self.document_type,
            correspondent=self.correspondent,
            customer_id=self.customer_id,
            document_number=self.document_number,
            document_date=self.document_date,
            fallback_filename=self.original_filename
        )
    
    # Deprecated: Für Backwards-Compatibility
    def generate_filename(self) -> str:
        """DEPRECATED: Use .generated_filename property instead"""
        return self.generated_filename
    
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