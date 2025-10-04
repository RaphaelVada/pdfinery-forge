from pathlib import Path
import shutil
from typing import List
import logging
import base64
from app.models import Document
from app.models import DocumentCollection

logger = logging.getLogger(__name__)


class LocalStorageService:
    """Service für lokale Dateisystem-basierte Dokumenten-Verarbeitung"""
    
    def __init__(
        self,
        data_in: Path = Path("/data/in"), 
        data_archive: Path = Path("/data/archive"),
        data_out: Path = Path("/data/out")
    ):
        self.data_in = data_in
        self.data_archive = data_archive
        self.data_out = data_out
        self.data_archive.mkdir(parents=True, exist_ok=True)
        self.data_out.mkdir(parents=True, exist_ok=True)
    
    def ingest_documents(self, collection: DocumentCollection) -> DocumentCollection:
        """
        Liest alle PDFs aus /data/in, erstellt Document-Objekte,
        verschiebt PDFs nach /data/archive, speichert Metadaten
        und befüllt die übergebene Collection
        """
        pdf_files = list(self.data_in.glob("*.pdf"))
        
        for pdf_path in pdf_files:
            doc = Document(original_filename=pdf_path.name)
            
            # PDF nach /data/archive verschieben
            archive_pdf = self.data_archive / f"{doc.id}.pdf"
            shutil.move(str(pdf_path), str(archive_pdf))
            
            # Document-Objekt als JSON speichern
            metadata_file = self.data_archive / f"{doc.id}.json"
            metadata_file.write_text(doc.model_dump_json(indent=2))
            
            # Zur Collection hinzufügen
            collection.add(doc)
            logger.info(f"Document {doc.id} ({doc.original_filename}) ingested")
        
        return collection
    
    def load_documents(self, collection: DocumentCollection) -> DocumentCollection:
        """
        Liest alle serialisierten Document-Objekte aus /data/archive
        und befüllt die übergebene Collection
        """
        json_files = list(self.data_archive.glob("*.json"))
        
        for json_path in json_files:
            try:
                json_data = json_path.read_text()
                doc = Document.model_validate_json(json_data)
                collection.add(doc)
                logger.info(f"Document {doc.id} geladen")
            except ValueError as e:
                # Doppelte UUID - überspringen
                logger.warning(f"Überspringe {json_path.name}: {e}")
                continue
            except Exception as e:
                # Fehlerhafte Dateien überspringen
                logger.error(f"Fehler beim Laden von {json_path.name}: {e}")
                continue
        
        return collection
    
    def update_metadata(self, document: Document) -> None:
        """
        Speichert aktualisierte Metadaten eines Documents im Archive
        """
        metadata_file = self.data_archive / f"{document.id}.json"
        metadata_file.write_text(document.model_dump_json(indent=2))
        logger.info(f"Metadaten aktualisiert für Document {document.id}")
    
    def save_to_output(self, document: Document) -> Path:
        """
        Speichert PDF mit generiertem Dateinamen nach /data/out.
        Falls bereits gespeichert, wird alte Datei gelöscht.
        Bei Namenskonflikten wird durchnummeriert: datei(1).pdf, datei(2).pdf, etc.
        """
        # Alte Datei löschen, falls vorhanden
        if document.is_saved:
            old_filename = document.current_filename
            old_path = self.data_out / old_filename
            if old_path.exists():
                old_path.unlink()
                logger.info(f"Alte Datei gelöscht: {old_filename}")
        
        # Quell-PDF im Archive
        source_pdf = self.data_archive / f"{document.id}.pdf"
        
        if not source_pdf.exists():
            raise FileNotFoundError(f"PDF nicht gefunden: {source_pdf}")
        
        # Ziel-Dateiname generieren
        target_filename = document.generate_filename()
        target_path = self.data_out / target_filename
        
        # Bei Konflikt durchnummerieren
        if target_path.exists():
            stem = target_path.stem  # Dateiname ohne Extension
            suffix = target_path.suffix  # .pdf
            counter = 1
            
            while target_path.exists():
                target_path = self.data_out / f"{stem}({counter}){suffix}"
                counter += 1
            
            logger.warning(f"Dateiname-Konflikt: Umbenannt zu {target_path.name}")
        
        # PDF kopieren
        shutil.copy2(str(source_pdf), str(target_path))
        
        # In saved_as History eintragen
        document.add_saved_filename(target_path.name)
        self.update_metadata(document)
        
        logger.info(f"Document {document.id} gespeichert nach {target_path}")
        return target_path
    
    def load_pdf_as_base64(self, document: Document) -> str:
        """
        Lädt PDF aus Archive als Base64-String.
        Geeignet für Anthropic Claude API und Web-Download.
        """
        pdf_path = self.data_archive / f"{document.id}.pdf"
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF nicht gefunden: {pdf_path}")
        
        pdf_bytes = pdf_path.read_bytes()
        base64_string = base64.b64encode(pdf_bytes).decode('utf-8')
        
        logger.debug(f"PDF {document.id} als Base64 geladen ({len(pdf_bytes)} bytes)")
        return base64_string