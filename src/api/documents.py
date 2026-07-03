from fastapi import APIRouter, Depends

from src.di import require_permission
from src.models import User


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.get("", summary="Получить список всех документов")
def get_documents(
    user: User = Depends(require_permission("document:read")),
):
    return {
        "user": user.email,
        "action": "document:read",
        "documents": [
            {"id": 1, "title": "Document 1"},
            {"id": 2, "title": "Document 2"},
        ],
    }


@router.post("", summary="Создать документ")
def create_document(
    user: User = Depends(require_permission("document:create")),
):
    return {
        "user": user.email,
        "action": "document:create",
        "detail": "Document created",
    }


@router.delete("/{document_id}", summary='Удалить документ')
def delete_document(
    document_id: int,
    user: User = Depends(require_permission("document:delete")),
):
    return {
        "user": user.email,
        "action": "document:delete",
        "detail": f"Document {document_id} deleted",
    }
