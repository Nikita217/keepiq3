from __future__ import annotations

import re
from contextlib import asynccontextmanager
from urllib.parse import urlsplit, urlunsplit

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.bot.runtime import configure_webhook, handle_webhook
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()


def normalize_origin(url: str) -> str:
    '''Reduce a configured URL to the exact origin string expected by CORS.'''
    parts = urlsplit(url)
    if not parts.scheme or not parts.netloc:
        return url.rstrip('/')
    return urlunsplit((parts.scheme, parts.netloc, '', '', ''))


def build_origin_regex(url: str) -> str | None:
    '''Allow Cloudflare Pages preview subdomains for the configured frontend host.'''
    parts = urlsplit(url)
    host = parts.hostname
    if not parts.scheme or not host:
        return None
    if host.endswith('.pages.dev'):
        return rf'{re.escape(parts.scheme)}://(?:[a-z0-9-]+\.)?{re.escape(host)}'
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await configure_webhook(app)
    yield


app = FastAPI(title=settings.app_name, debug=settings.app_debug, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        normalize_origin(settings.frontend_base_url),
        normalize_origin(settings.app_base_url),
        'http://localhost:5173',
    ],
    allow_origin_regex=build_origin_regex(settings.frontend_base_url),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.post(settings.telegram_webhook_path)
async def telegram_webhook(request: Request):
    return await handle_webhook(request)
