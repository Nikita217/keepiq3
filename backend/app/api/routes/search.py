from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.schemas.search import SearchResponse
from app.search.service import SearchService
from app.services.ai_pipeline import AIProcessingService

router = APIRouter()
service = SearchService()
ai_service = AIProcessingService()


@router.get("", response_model=SearchResponse)
async def search(q: str = Query(min_length=2), user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> SearchResponse:
    query_embedding = await ai_service.ai_client.embed(q)
    results = await service.search(session, user_id=user.id, query=q, query_embedding=query_embedding)
    return SearchResponse(query=q, results=results)
