# KeepiQ MVP

KeepiQ is a multi-user Telegram bot and Telegram Mini App for turning messy incoming information into structured tasks, reminders, lists, and a safe inbox.

The repository contains:

- `backend/`: FastAPI API, aiogram bot, scheduler worker, SQLAlchemy models, AI pipeline.
- `frontend/`: React + TypeScript + Tailwind Telegram Mini App.
- `docs/`: launch, deployment and codebase guides.
- `tests/`: backend smoke tests for the MVP flows.

## Documentation map

- Local launch and first-run guide: `docs/RUN_LOCAL.md`
- Deployment guide: `docs/DEPLOY.md`
- Full architecture and file-by-file guide: `docs/CODEBASE_GUIDE.md`

## What you need before running

- Windows, macOS or Linux
- Python 3.11+ recommended
- Node.js 20+
- PostgreSQL 15+
- Telegram bot token from BotFather
- OpenAI API key

## Quick start

1. Copy `.env.example` to `.env`.
2. Copy `frontend/.env.example` to `frontend/.env`.
3. Fill in at least these backend variables in `.env`:
   - `DATABASE_URL`
   - `ALEMBIC_DATABASE_URL`
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
4. Start PostgreSQL.
5. Install backend dependencies and apply migrations:

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
alembic upgrade head
```

6. Start the API:

```bash
uvicorn app.main:app --reload
```

7. In a second terminal, start the Telegram bot in polling mode:

```bash
cd backend
. .venv/Scripts/activate
python -m app.bot.run_polling
```

8. In a third terminal, start the worker:

```bash
cd backend
. .venv/Scripts/activate
python -m app.workers.run
```

9. Start the Mini App frontend:

```bash
cd frontend
npm install
npm run dev
```

10. Open the frontend locally at `http://localhost:5173`.

For a full walkthrough, troubleshooting, Telegram setup and first-message test flow, read `docs/RUN_LOCAL.md`.

## Test commands

Backend smoke tests:

```bash
cd backend
. .venv/Scripts/activate
pytest -q ../tests/backend
```

Frontend production build:

```bash
cd frontend
npm run build
```

## Production shape

- API + webhook: Render web service
- Worker: Render background service
- Frontend: Cloudflare Pages or Render static hosting
- Database: PostgreSQL

Detailed production setup: `docs/DEPLOY.md`.
