from fastapi import APIRouter

from app.api.routes import auth, calendar, health, inbox, lists, search, tasks, today

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(today.router, prefix="/today", tags=["today"])
api_router.include_router(inbox.router, prefix="/inbox", tags=["inbox"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(lists.router, prefix="/lists", tags=["lists"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
