from app.models import DocumentCollection
from app.services.local_storage_service import LocalStorageService

# Globale Instanzen
collection = DocumentCollection()
storage = LocalStorageService()


def get_collection() -> DocumentCollection:
    """Dependency für DocumentCollection"""
    return collection


def get_storage() -> LocalStorageService:
    """Dependency für LocalStorageService"""
    return storage