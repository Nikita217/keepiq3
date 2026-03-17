from __future__ import annotations

import math
import re
from collections import Counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inbox_item import InboxItem
from app.models.task import Task
from app.models.task_list import TaskList
from app.schemas.search import SearchResultItem

TOKEN_RE = re.compile(r"[\wа-яА-ЯёЁ]{2,}")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


def lexical_score(query: str, document: str) -> float:
    q_tokens = tokenize(query)
    d_tokens = tokenize(document)
    if not q_tokens or not d_tokens:
        return 0.0
    q_count = Counter(q_tokens)
    d_count = Counter(d_tokens)
    overlap = sum(min(count, d_count[token]) for token, count in q_count.items())
    return overlap / math.sqrt(len(q_tokens) * len(d_tokens))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


class SearchService:
    async def search(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        query: str,
        query_embedding: list[float] | None = None,
        limit: int = 20,
    ) -> list[SearchResultItem]:
        task_result = await session.execute(select(Task).where(Task.user_id == user_id).limit(200))
        list_result = await session.execute(select(TaskList).where(TaskList.user_id == user_id).limit(100))
        inbox_result = await session.execute(select(InboxItem).where(InboxItem.user_id == user_id).limit(200))

        candidates: list[SearchResultItem] = []
        for task in task_result.scalars().all():
            text = " ".join(filter(None, [task.title, task.description, task.normalized_source_text]))
            score = lexical_score(query, text)
            if query_embedding and task.embedding:
                score += cosine_similarity(query_embedding, task.embedding)
            if score > 0:
                candidates.append(SearchResultItem(kind="task", id=task.id, title=task.title, subtitle=task.description, score=score, matched_text=text[:280]))

        for task_list in list_result.scalars().all():
            text = " ".join(filter(None, [task_list.title, task_list.description, task_list.normalized_source_text]))
            score = lexical_score(query, text)
            if query_embedding and task_list.embedding:
                score += cosine_similarity(query_embedding, task_list.embedding)
            if score > 0:
                candidates.append(SearchResultItem(kind="list", id=task_list.id, title=task_list.title, subtitle=task_list.description, score=score, matched_text=text[:280]))

        for inbox in inbox_result.scalars().all():
            text = " ".join(filter(None, [inbox.ai_summary, inbox.normalized_text, inbox.extracted_text, inbox.raw_text]))
            score = lexical_score(query, text)
            if query_embedding and inbox.embedding:
                score += cosine_similarity(query_embedding, inbox.embedding)
            if score > 0:
                title = inbox.ai_summary or (inbox.normalized_text or inbox.raw_text or "Входящее")[:80]
                candidates.append(SearchResultItem(kind="inbox", id=inbox.id, title=title, subtitle=inbox.ai_detected_type, score=score, matched_text=text[:280]))

        candidates.sort(key=lambda item: item.score, reverse=True)
        return candidates[:limit]
