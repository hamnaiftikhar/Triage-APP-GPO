# Telemedicine Triage MVP

A small full-stack MVP for telemedicine request triage. The system accepts plain-text requests, classifies them into a simple clinical or operational structure, prioritises them, stores them in PostgreSQL, and shows both the live queue and the audit trail in a React dashboard.

## What it does

- Accepts request text from the frontend or API.
- Classifies each request using LangGraph plus OpenAI, with a heuristic fallback when no key is present.
- Routes requests into a clinical or operational queue.
- Stores requests and audit events in PostgreSQL.
- Shows a queue view and audit trail for clinical support.
- Applies validation, rate limiting, and audit logging.

## Stack

- Backend: Python, FastAPI, LangGraph, Pydantic, Psycopg
- Frontend: React, Vite, Tailwind CSS
- Database: PostgreSQL
- LLM: OpenAI via the Python SDK, with fallback heuristics

## Project Structure

- [backend/](backend) - FastAPI backend, LangGraph workflow, PostgreSQL persistence
- [frontend/](frontend) - React dashboard

## Local Setup

### 1. Create backend env

Create [backend/.env](backend/.env) with:

```env
APP_NAME=Telemedicine Triage MVP
DATABASE_URL=postgresql://triage:triage@localhost:5432/triage
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 2. Start PostgreSQL

Use your local PostgreSQL instance and make sure the `triage` database and user exist.

### 3. Install backend dependencies

```bash
cd backend
/Users/umar/triage-app/.venv/bin/python -m pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

### 5. Run the app

Backend:

```bash
cd /Users/umar/triage-app
/Users/umar/triage-app/.venv/bin/python -m uvicorn app.main:app --port 8000 --app-dir /Users/umar/triage-app/backend
```

Frontend:

```bash
cd frontend
npm run dev
```

## API Endpoints

- `POST /submit-request` - submit a triage request
- `GET /queue` - list queued requests
- `POST /approve-request` - approve a request
- `GET /audit-log` - inspect recent triage actions

## Workflow Summary

```mermaid
flowchart LR
  A[Patient request from web/API] --> B[Validation + rate limit]
  B --> C[LangGraph classifier]
  C --> D[Clinical or operational grouping]
  D --> E[Priority assignment P1-P3]
  E --> F[Route to queue]
  F --> G[Persist in PostgreSQL]
  G --> H[Audit log]
  H --> I[Clinical support dashboard]
```

## Notes

- The workflow is implemented code-first rather than in n8n/Zapier.
- That automation-platform layer can be added later if required.
- The current UI is a pragmatic slice for intake, queue visibility, and audit visibility.

## Next steps with more time

- Add more intake channels such as email and portal webhooks.
- Add patient-facing status updates.
- Add authentication and role-based access.
- Add outbound notifications by email or SMS.
- Add a proper automation layer in n8n or a similar tool.
