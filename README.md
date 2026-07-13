# Telemedicine Triage MVP

A small full-stack MVP for telemedicine request triage. The system accepts plain-text requests, classifies them into a simple clinical or operational structure, prioritises them, stores them in PostgreSQL, and shows both the live queue and the audit trail in a React dashboard.

## What it does

- Accepts request text from the frontend or API.
- Classifies each request using LangGraph plus OpenAI, with a heuristic fallback when no key is present.
- Routes requests into a clinical or operational queue.
- Stores requests and audit events in PostgreSQL.
- Shows a queue view and audit trail for clinical support.
- Applies validation, rate limiting, and audit logging.

## How the App Works

Below is the end-to-end flow of a single triage request, from patient submission to clinical review.

```mermaid
sequenceDiagram
    participant Patient
    participant Frontend as React Dashboard
    participant API as FastAPI Backend
    participant Guard as Guardrails
    participant LG as LangGraph Workflow
    participant LLM as OpenAI / Heuristic
    participant DB as PostgreSQL

    Patient->>Frontend: Types request text
    Frontend->>API: POST /submit-request
    API->>Guard: Validate length + rate limit
    Guard-->>API: Pass
    API->>LG: Invoke triage graph
    LG->>LLM: Classify text
    LLM-->>LG: category + urgency
    LG->>LG: Route to queue
    LG-->>API: Classified state
    API->>DB: Save request + audit event
    API-->>Frontend: Return request reference
    Frontend-->>Patient: Show confirmation + reference ID
```

### Step 1 — Patient submits a request
A patient (or staff member) types a plain-text message into the web form, for example: *"I have severe chest pain and shortness of breath"*. The frontend sends this to `POST /submit-request`.

### Step 2 — Validation & rate limiting
The backend checks that the text is not empty, not too long, and that the caller has not exceeded the rate limit. Malformed or abusive requests are rejected before they reach the AI pipeline.

### Step 3 — Prompt-injection filtering
Before the request reaches the LLM, a pre-filter scans the text for known prompt-injection signatures (e.g., *"ignore all previous instructions"*). If detected, the request is safely classified as operational/P3 without ever being sent to the model.

### Step 4 — AI classification via LangGraph
The validated text enters a **LangGraph state machine** with two nodes:

1. **Classifier Node** — Sends the text to OpenAI (`gpt-4o-mini`) using structured output parsing. The model returns:
   - **Category**: `clinical` or `operational`
   - **Urgency**: `P1` (emergency), `P2` (standard), or `P3` (low priority)
   - If no OpenAI key is configured, a **keyword-based heuristic** fallback handles classification instead.

2. **Router Node** — Based on the category, assigns the request to either the **Clinical Queue** or the **Operations Queue**.

### Step 5 — Persistence in PostgreSQL
The fully classified request (with its category, urgency, status, and queue assignment) is saved to the `triage_requests` table. An audit event is also written to the `triage_audit_log` table, recording the action, the client IP, and all classification details.

### Step 6 — Clinical staff reviews the queue
Staff members open the dashboard, authenticate with a staff token, and see the live queue sorted by creation time. They can:
- **Approve** a request to mark it as processed.
- **Delete** a request to remove it from the queue.
- **View the audit trail** to see a history of all submit, approve, and delete actions.

### Step 7 — Patient checks status
After submission, the patient receives a unique **request reference ID**. They can paste this ID into the status lookup section on the dashboard to check the current state of their request at any time.


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
/Users/hamna/triage-app/.venv/bin/python -m pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

### 5. Run the app

Backend:

```bash
cd /Users/hamna/triage-app
/Users/hamna/triage-app/.venv/bin/python -m uvicorn app.main:app --port 8000 --app-dir /Users/hamna/triage-app/backend
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
