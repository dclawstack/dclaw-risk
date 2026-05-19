from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Document(Base, UUIDPKMixin, TimestampMixin):
    """A knowledge-base document the Copilot can retrieve from.

    Storage is plain text; retrieval is TF-IDF cosine similarity computed on
    demand. For production scale this would move to pgvector + embeddings,
    but TF-IDF is a clean, fully-local first cut.
    """

    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
