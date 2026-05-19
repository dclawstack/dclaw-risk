"""TF-IDF retriever over the documents table.

Computes the index per-query (cheap for the document counts we expect at
P0/P1 scale). A vector-DB-backed retriever can swap in via
`app.services.llm.set_retriever()` without touching call sites.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]+")


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text)]


@dataclass
class Hit:
    document_id: str
    title: str
    score: float
    snippet: str


class TfidfRetriever:
    """Tiny dependency-free TF-IDF retriever scoped to a single SQL session."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def retrieve(self, query: str, k: int = 5) -> list[str]:
        hits = await self.search(query, k=k)
        return [
            f"[{h.title}] {h.snippet}" for h in hits if h.score > 0
        ]

    async def search(self, query: str, k: int = 5) -> list[Hit]:
        docs = (await self.db.execute(select(Document))).scalars().all()
        if not docs:
            return []

        tokenised = [_tokenize(d.content) for d in docs]
        n = len(docs)
        df: Counter[str] = Counter()
        for toks in tokenised:
            for term in set(toks):
                df[term] += 1
        idf = {
            t: math.log((1 + n) / (1 + freq)) + 1 for t, freq in df.items()
        }

        def vec(toks: list[str]) -> dict[str, float]:
            tf = Counter(toks)
            length = max(1, sum(tf.values()))
            return {t: (c / length) * idf.get(t, 0.0) for t, c in tf.items()}

        q_vec = vec(_tokenize(query))
        if not q_vec:
            return []

        results: list[Hit] = []
        for doc, toks in zip(docs, tokenised, strict=True):
            d_vec = vec(toks)
            score = _cosine(q_vec, d_vec)
            if score <= 0:
                continue
            snippet = doc.content[:240].replace("\n", " ").strip()
            results.append(
                Hit(
                    document_id=str(doc.id),
                    title=doc.title,
                    score=score,
                    snippet=snippet,
                )
            )

        results.sort(key=lambda h: h.score, reverse=True)
        return results[:k]


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    num = sum(a[t] * b[t] for t in common)
    da = math.sqrt(sum(v * v for v in a.values()))
    db_ = math.sqrt(sum(v * v for v in b.values()))
    if da == 0 or db_ == 0:
        return 0.0
    return num / (da * db_)
