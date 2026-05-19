from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.services.retriever import TfidfRetriever

router = APIRouter()


class DocumentIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    source: str | None = None


class DocumentOut(BaseModel):
    id: UUID
    title: str
    source: str | None
    excerpt: str
    created_at: str


@router.get("")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    docs = (
        await db.execute(select(Document).order_by(Document.created_at.desc()))
    ).scalars().all()
    return {
        "items": [
            {
                "id": str(d.id),
                "title": d.title,
                "source": d.source,
                "excerpt": d.content[:200],
                "created_at": d.created_at.isoformat(),
            }
            for d in docs
        ],
        "total": len(docs),
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    doc = Document(
        title=payload.title, content=payload.content, source=payload.source
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return {"id": str(doc.id), "title": doc.title}


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    doc = (
        await db.execute(select(Document).where(Document.id == doc_id))
    ).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    await db.delete(doc)
    await db.commit()


@router.get("/search")
async def search_documents(
    q: str,
    k: int = 5,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Verify retrieval results before they hit the Copilot prompt."""
    hits = await TfidfRetriever(db).search(q, k=k)
    return {
        "query": q,
        "hits": [
            {
                "document_id": h.document_id,
                "title": h.title,
                "score": round(h.score, 4),
                "snippet": h.snippet,
            }
            for h in hits
        ],
    }
