# Environment Templates

Этот файл нужен как готовая шпаргалка для прод-настроек.

Сценарий проекта:

- `keepiq-api` -> Render Web Service
- `keepiq-worker` -> Render Background Worker
- `frontend` -> Cloudflare Pages
- `database` -> Render PostgreSQL

Ниже даны готовые шаблоны.
Менять нужно только то, что отмечено как `CHANGE_ME` или зависит от твоих реальных доменов, токенов и базы.

## 1. Render Web Service: `keepiq-api`

Сервис:

- Name: `keepiq-api`
- Environment: `Python`
- Branch: `main`
- Root Directory: `backend`
- Build Command: `pip install -e .[dev] && alembic upgrade head`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Environment Variables:

```env
APP_NAME=KeepiQ
APP_ENV=production
APP_DEBUG=false
API_PREFIX=/api/v1

SECRET_KEY=CHANGE_ME_LONG_RANDOM_SECRET

DATABASE_URL=CHANGE_ME_RENDER_POSTGRES_ASYNCPG_URL
ALEMBIC_DATABASE_URL=CHANGE_ME_RENDER_POSTGRES_PSYCOPG_URL

APP_BASE_URL=https://keepiq-api.onrender.com
FRONTEND_BASE_URL=https://CHANGE_ME.pages.dev
TELEGRAM_MINI_APP_URL=https://CHANGE_ME.pages.dev

TELEGRAM_BOT_TOKEN=CHANGE_ME
TELEGRAM_BOT_USERNAME=CHANGE_ME
TELEGRAM_USE_WEBHOOK=true
TELEGRAM_WEBHOOK_SECRET=CHANGE_ME_RANDOM_WEBHOOK_SECRET
TELEGRAM_WEBHOOK_PATH=/telegram/webhook

DEFAULT_TIMEZONE=Europe/Moscow
DEFAULT_DATE_TIME=10:00
MORNING_SUMMARY_TIME=09:00
EVENING_SUMMARY_TIME=21:00
EVENT_REMINDER_HOURS_BEFORE=3

ALLOW_DEV_AUTH=false
DEV_TELEGRAM_USER_ID=100001
DEV_TELEGRAM_USERNAME=demo_user
DEV_TELEGRAM_FIRST_NAME=Demo

OPENAI_API_KEY=CHANGE_ME
OPENAI_REASONING_MODEL=gpt-5-mini
OPENAI_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_VISION_MODEL=gpt-4.1-mini

SEARCH_EMBEDDINGS_ENABLED=false
WORKER_POLL_INTERVAL_SECONDS=30
LOG_LEVEL=INFO
```

## 2. Render Background Worker: `keepiq-worker`

Сервис:

- Name: `keepiq-worker`
- Environment: `Python`
- Branch: `main`
- Root Directory: `backend`
- Build Command: `pip install -e .[dev]`
- Start Command: `python -m app.workers.run`

Environment Variables:

Используй почти тот же набор, что и у API.
Проще всего скопировать всё из `keepiq-api` и вставить в `keepiq-worker`.

```env
APP_NAME=KeepiQ
APP_ENV=production
APP_DEBUG=false
API_PREFIX=/api/v1

SECRET_KEY=CHANGE_ME_LONG_RANDOM_SECRET

DATABASE_URL=CHANGE_ME_RENDER_POSTGRES_ASYNCPG_URL
ALEMBIC_DATABASE_URL=CHANGE_ME_RENDER_POSTGRES_PSYCOPG_URL

APP_BASE_URL=https://keepiq-api.onrender.com
FRONTEND_BASE_URL=https://CHANGE_ME.pages.dev
TELEGRAM_MINI_APP_URL=https://CHANGE_ME.pages.dev

TELEGRAM_BOT_TOKEN=CHANGE_ME
TELEGRAM_BOT_USERNAME=CHANGE_ME
TELEGRAM_USE_WEBHOOK=true
TELEGRAM_WEBHOOK_SECRET=CHANGE_ME_RANDOM_WEBHOOK_SECRET
TELEGRAM_WEBHOOK_PATH=/telegram/webhook

DEFAULT_TIMEZONE=Europe/Moscow
DEFAULT_DATE_TIME=10:00
MORNING_SUMMARY_TIME=09:00
EVENING_SUMMARY_TIME=21:00
EVENT_REMINDER_HOURS_BEFORE=3

ALLOW_DEV_AUTH=false
DEV_TELEGRAM_USER_ID=100001
DEV_TELEGRAM_USERNAME=demo_user
DEV_TELEGRAM_FIRST_NAME=Demo

OPENAI_API_KEY=CHANGE_ME
OPENAI_REASONING_MODEL=gpt-5-mini
OPENAI_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_VISION_MODEL=gpt-4.1-mini

SEARCH_EMBEDDINGS_ENABLED=false
WORKER_POLL_INTERVAL_SECONDS=30
LOG_LEVEL=INFO
```

## 3. Cloudflare Pages: frontend

Проект:

- Framework preset: `Vite`
- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Branch: `main`

Environment Variables:

```env
VITE_API_BASE_URL=https://keepiq-api.onrender.com/api/v1
```

## 4. Render PostgreSQL

Когда создашь Postgres на Render, он даст обычную connection string.

Тебе нужны две версии:

### Для `DATABASE_URL`

Используй asyncpg-формат:

```env
postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME
```

### Для `ALEMBIC_DATABASE_URL`

Используй psycopg-формат:

```env
postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
```

Если Render покажет URL в виде:

```env
postgres://USER:PASSWORD@HOST:5432/DBNAME
```

то просто преобразуй так:

- `DATABASE_URL` -> замени `postgres://` на `postgresql+asyncpg://`
- `ALEMBIC_DATABASE_URL` -> замени `postgres://` на `postgresql+psycopg://`

## 5. Что именно нужно поменять руками

Обязательно поменяй:

- `SECRET_KEY`
- `DATABASE_URL`
- `ALEMBIC_DATABASE_URL`
- `FRONTEND_BASE_URL`
- `TELEGRAM_MINI_APP_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `TELEGRAM_WEBHOOK_SECRET`
- `OPENAI_API_KEY`
- `VITE_API_BASE_URL`

## 6. Что можно оставить как есть

Оставляй без изменений, если нет отдельной причины трогать:

- `APP_NAME=KeepiQ`
- `APP_ENV=production`
- `APP_DEBUG=false`
- `API_PREFIX=/api/v1`
- `DEFAULT_TIMEZONE=Europe/Moscow`
- `DEFAULT_DATE_TIME=10:00`
- `MORNING_SUMMARY_TIME=09:00`
- `EVENING_SUMMARY_TIME=21:00`
- `EVENT_REMINDER_HOURS_BEFORE=3`
- `ALLOW_DEV_AUTH=false`
- `OPENAI_REASONING_MODEL=gpt-5-mini`
- `OPENAI_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe`
- `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`
- `OPENAI_VISION_MODEL=gpt-4.1-mini`
- `SEARCH_EMBEDDINGS_ENABLED=false`
- `WORKER_POLL_INTERVAL_SECONDS=30`
- `LOG_LEVEL=INFO`

## 7. После того как всё вставишь

Порядок такой:

1. Создать Render Postgres
2. Создать `keepiq-api`
3. Создать `keepiq-worker`
4. Создать Cloudflare Pages frontend
5. Вставить Cloudflare URL в:
   - `FRONTEND_BASE_URL`
   - `TELEGRAM_MINI_APP_URL`
6. Вставить Render backend URL в:
   - `APP_BASE_URL`
   - `VITE_API_BASE_URL`
7. После деплоя настроить BotFather:
   - Mini App URL = Cloudflare Pages URL
   - webhook = `https://keepiq-api.onrender.com/telegram/webhook` или твой реальный Render-домен

## 8. Самый короткий прод-набор

Если нужно совсем коротко, минимально критичны вот эти переменные:

```env
SECRET_KEY=CHANGE_ME
DATABASE_URL=CHANGE_ME
ALEMBIC_DATABASE_URL=CHANGE_ME
APP_BASE_URL=https://keepiq-api.onrender.com
FRONTEND_BASE_URL=https://CHANGE_ME.pages.dev
TELEGRAM_MINI_APP_URL=https://CHANGE_ME.pages.dev
TELEGRAM_BOT_TOKEN=CHANGE_ME
TELEGRAM_BOT_USERNAME=CHANGE_ME
TELEGRAM_USE_WEBHOOK=true
TELEGRAM_WEBHOOK_SECRET=CHANGE_ME
TELEGRAM_WEBHOOK_PATH=/telegram/webhook
OPENAI_API_KEY=CHANGE_ME
```
