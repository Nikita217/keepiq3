# Local Launch Guide

This guide is the fastest path from a fresh checkout to a working local KeepiQ instance.

## 1. Services in the project

For local MVP work you will run 4 things:

1. PostgreSQL
2. FastAPI backend
3. Telegram bot in polling mode
4. Worker for reminders, summaries and retry jobs
5. Frontend Mini App

Yes, that is effectively 5 processes if you count PostgreSQL separately.

## 2. Required software

Install these first:

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- PostgreSQL 15 or newer
- Git

Recommended on Windows:

- PowerShell
- Git for Windows

## 3. Get the project

If you already have the folder, skip this section.

```bash
git clone https://github.com/Nikita217/keepiq3.git
cd keepiq3
```

## 4. Create env files

### Backend env

Create `.env` in the project root from `.env.example`.

PowerShell:

```powershell
Copy-Item .env.example .env
```

Minimum fields to fill:

- `DATABASE_URL`
- `ALEMBIC_DATABASE_URL`
- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`

Recommended local values:

```env
APP_NAME=KeepiQ
APP_ENV=development
APP_DEBUG=true
APP_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5173
API_PREFIX=/api/v1
SECRET_KEY=change-me-local-secret

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/keepiq
ALEMBIC_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/keepiq

TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_USE_WEBHOOK=false
TELEGRAM_WEBHOOK_SECRET=keepiq-webhook-secret
TELEGRAM_WEBHOOK_PATH=/telegram/webhook
TELEGRAM_MINI_APP_URL=http://localhost:5173

DEFAULT_TIMEZONE=Europe/Moscow
ALLOW_DEV_AUTH=true
DEV_TELEGRAM_USER_ID=100001
DEV_TELEGRAM_USERNAME=demo_user
DEV_TELEGRAM_FIRST_NAME=Demo

OPENAI_API_KEY=your_openai_key_here
OPENAI_REASONING_MODEL=gpt-5-mini
OPENAI_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_VISION_MODEL=gpt-4.1-mini
```

### Frontend env

Create `frontend/.env` from `frontend/.env.example`.

```powershell
Copy-Item frontend/.env.example frontend/.env
```

Default local frontend env:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 5. Start PostgreSQL

Create database `keepiq`.

Example with `psql`:

```sql
CREATE DATABASE keepiq;
```

If your local username/password are different, update both database URLs in `.env`.

## 6. Install backend and run migrations

Open terminal 1:

```powershell
cd backend
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -e .[dev]
alembic upgrade head
```

What this does:

- creates the virtual environment
- installs FastAPI, aiogram, SQLAlchemy, Alembic, OpenAI client and test dependencies
- creates all MVP tables in PostgreSQL

## 7. Start backend API

Still in terminal 1:

```powershell
uvicorn app.main:app --reload
```

Expected local URL:

- API root: `http://localhost:8000`
- Health endpoint: `http://localhost:8000/api/v1/health`

Quick check:

```powershell
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{"status":"ok"}
```

## 8. Start Telegram bot in polling mode

Open terminal 2:

```powershell
cd backend
. .venv\Scripts\Activate.ps1
python -m app.bot.run_polling
```

Important:

- local development uses polling
- `.env` must contain `TELEGRAM_USE_WEBHOOK=false`
- `TELEGRAM_BOT_TOKEN` must be valid

What should happen:

- the bot connects to Telegram
- you can message the bot directly in Telegram
- no public URL is needed for this local mode

## 9. Start worker

Open terminal 3:

```powershell
cd backend
. .venv\Scripts\Activate.ps1
python -m app.workers.run
```

Why the worker matters:

- retries failed AI processing
- sends reminders
- sends morning summaries
- sends evening summaries

If you do not run the worker, the basic bot and API will still work, but reminders and scheduled flows will not fire.

## 10. Start frontend Mini App

Open terminal 4:

```powershell
cd frontend
npm install
npm run dev
```

Expected local URL:

- `http://localhost:5173`

Local auth behavior:

- if opened outside Telegram and `ALLOW_DEV_AUTH=true`, the frontend uses `/auth/dev`
- this lets you test the Mini App without Telegram WebApp signature locally

## 11. First local verification flow

Use this exact order.

### API check

Open:

- `http://localhost:8000/api/v1/health`

You should get `{"status":"ok"}`.

### Mini App check

Open:

- `http://localhost:5173`

You should see the app shell and tabs.

### Bot check

In Telegram:

1. Open your bot
2. Send `/start`
3. Send a text like `завтра купить батарейки`

Expected behavior:

- inbox item is created
- bot answers with a short human message
- bot shows exactly 4 inline buttons
- one button is always `Оставить во входящих`

### Worker check

Send a message that has a short due time or manually edit DB for a near reminder.

Expected behavior:

- worker eventually sends a reminder message
- reminder message shows 4 quick actions

## 12. How to test voice and screenshot flows

### Voice

1. Send a voice message to the bot
2. Backend downloads it temporarily
3. OpenAI transcription runs if `OPENAI_API_KEY` is set
4. Extracted text is saved into Inbox
5. AI understanding proposes task/list/inbox actions

### Screenshot or image

1. Send a screenshot or photo to the bot
2. Backend downloads image temporarily
3. Vision/OCR extraction runs if `OPENAI_API_KEY` is set
4. Extracted text is saved into Inbox
5. AI understanding proposes next actions

If OpenAI is unavailable:

- the original message still becomes an Inbox item
- processing status can move to retry flow
- nothing is lost

## 13. Useful development commands

### Backend tests

```powershell
cd backend
. .venv\Scripts\Activate.ps1
pytest -q ..\tests\backend
```

### Frontend production build

```powershell
cd frontend
npm run build
```

### Compile check for Python files

```powershell
cd backend
. .venv\Scripts\Activate.ps1
python -m compileall app
```

## 14. Typical problems and fixes

### `python` is not recognized

Use the full Python launcher or install Python into PATH.

Try:

```powershell
py --version
```

or:

```powershell
py -3.11 -m venv .venv
```

### `psycopg` or `asyncpg` connection errors

Check:

- PostgreSQL is running
- database `keepiq` exists
- username/password in `.env` are correct
- ports are correct

### `alembic upgrade head` fails

Usually one of these:

- wrong `ALEMBIC_DATABASE_URL`
- database not created yet
- missing dependencies in venv

### Bot does not answer in Telegram

Check:

- `TELEGRAM_BOT_TOKEN` is valid
- `python -m app.bot.run_polling` is running
- the bot is not simultaneously in webhook mode elsewhere

If the bot was deployed before, clear webhook locally by running polling entrypoint first. The app already does `delete_webhook()` before polling starts.

### Mini App does not load locally

Check:

- backend is running on port 8000
- frontend is running on port 5173
- `frontend/.env` points to the correct API base URL
- `ALLOW_DEV_AUTH=true` in root `.env`

### AI features do not work

Check:

- `OPENAI_API_KEY` is set
- you installed backend dependencies
- the model ids in `.env` are valid for your account

Without AI, the project still keeps messages in Inbox and uses fallback logic.

## 15. Telegram setup for local development

For local polling mode you only need:

- a bot token from BotFather
- a direct chat with the bot

You do not need:

- webhook
- public tunnel
- deployed frontend

For real Mini App testing inside Telegram later you will want a deployed frontend URL and Telegram domain setup. That is described in `docs/DEPLOY.md`.

## 16. Suggested terminal layout

Use four terminals:

1. `backend API`
2. `bot polling`
3. `worker`
4. `frontend`

That makes debugging much easier because logs stay separated.

## 17. What to read next

- deployment: `docs/DEPLOY.md`
- architecture and every file: `docs/CODEBASE_GUIDE.md`
