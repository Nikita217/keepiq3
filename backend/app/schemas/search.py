from pydantic import BaseModel


class SearchResultItem(BaseModel):
    kind: str
    id: int
    title: str
    subtitle: str | None
    score: float
    matched_text: str | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
