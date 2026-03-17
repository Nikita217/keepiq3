# Deployment Guide

## Target topology

MVP deployment is split into three services:

1. `keepiq-api` on Render
2. `keepiq-worker` on Render
3. `frontend` on Cloudflare Pages or Render static hosting

PostgreSQL should be managed separately. The app is written to use Postgres in production and SQLite only for tests or ultra-light local runs.

## Environment variables

Backend variables come from the root `.env.example`.

Required in production:

- `DATABASE_URL`
- `ALEMBIC_DATABASE_URL`
- `SECRET_KEY`
- `TELEGRAM_BOT_TOKEN`
- `APP_BASE_URL`
- `FRONTEND_BASE_URL`
- `TELEGRAM_MINI_APP_URL`
- `OPENAI_API_KEY`

Recommended:

- `TELEGRAM_USE_WEBHOOK=true`
- `OPENAI_REASONING_MODEL=gpt-5-mini`
- `OPENAI_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe`
- `OPENAI_VISION_MODEL=gpt-4.1-mini`
- `SEARCH_EMBEDDINGS_ENABLED=true`

Frontend variables:

- `VITE_API_BASE_URL`

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

### Bot polling

```bash
cd backend
python -m app.bot.run_polling
```

### Worker

```bash
cd backend
python -m app.workers.run
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Render deployment

Use the included `render.yaml`.

### API service

- Root directory: `backend`
- Build command: `pip install -e .[dev] && alembic upgrade head`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Worker service

- Root directory: `backend`
- Build command: `pip install -e .[dev]`
- Start command: `python -m app.workers.run`

### Optional polling service

`keepiq-bot-polling` exists in `render.yaml` as a non-default fallback for debugging. Production should normally use the webhook through the API service.

## Telegram setup

1. Create the bot with BotFather.
2. Set the Mini App button URL to your deployed frontend.
3. Set the domain for Telegram WebApp.
4. Point webhook to `https://your-api-domain/telegram/webhook`.
5. Store the bot token in `TELEGRAM_BOT_TOKEN`.

Manual webhook command:

```bash
cd backend
python scripts/set_webhook.py
```

## Cloudflare Pages deployment

Recommended for frontend:

- Build command: `npm run build`
- Build output: `dist`
- Environment variable: `VITE_API_BASE_URL=https://your-api-domain/api/v1`

Because the app uses `HashRouter`, static hosting does not need special SPA rewrite rules.

## Production checklist

- `ALLOW_DEV_AUTH=false`
- `TELEGRAM_USE_WEBHOOK=true`
- TLS enabled on both API and frontend domains
- Postgres backups enabled
- OpenAI key configured
- Telegram Mini App domain registered in BotFather
- Health check responding at `/api/v1/health`

## Operational notes

- If OpenAI fails, inbox items are still stored and marked for retry.
- The worker retries AI processing every 3 minutes.
- Reminder delivery runs every minute.
- Morning and evening summaries run every 15 minutes and check each user's local timezone.
- Search works without embeddings; embeddings only improve reranking.
