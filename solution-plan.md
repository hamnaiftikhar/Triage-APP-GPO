# Solution Plan

## Problem understanding

The service receives mixed telemedicine requests from multiple channels. Some are clinical and some are operational, and the work needs to be grouped, prioritised, routed, and tracked consistently. The biggest risk is not simply classification, but creating a stable internal structure that a small team can understand and operate.

## Proposed workflow

1. Requests arrive from web, email, phone transcription, or future channel integrations.
2. The system validates the text and applies rate limiting.
3. A LangGraph workflow classifies the request into a small internal schema.
4. The request is grouped into either clinical or operational work.
5. Urgency is assigned as P1, P2, or P3.
6. The request is routed to the appropriate queue.
7. The request and audit event are stored in PostgreSQL.
8. Clinical support reviews the queue in the dashboard.
9. Staff can approve requests, with every action recorded in the audit log.

## Grouping logic

The grouping model is intentionally small:

- Category: clinical or operational
- Urgency: P1, P2, or P3
- Queue: Clinical Queue or Operations Queue

This is deliberate. A small, stable taxonomy is easier to maintain than a large, brittle classification tree. The groupings are broad enough to handle mixed requests but still actionable for support staff. The classifier uses OpenAI when available and falls back to simple heuristics for reliability.

## Tooling choices

- FastAPI: lightweight API layer with clear request validation.
- LangGraph: explicit workflow structure that can grow into more steps later.
- PostgreSQL: reliable audit trail and queue storage.
- React + Tailwind: compact dashboard for queue visibility.
- Psycopg: simple and direct PostgreSQL integration.

## Guardrails

- Request length limits prevent overly large payloads.
- Rate limiting reduces accidental or abusive repeated submissions.
- Audit logging records every submit and approve action.
- The classifier falls back to heuristics when the LLM is unavailable.

## Assumptions

- The initial MVP is for clinical support visibility, not patient self-service.
- Notifications to patients are out of scope for this slice.
- Automation-platform integration is deferred, but the workflow is structured so it can be added later.
- Dummy data is acceptable for showing the queue and UI behavior.

## What I would do next

- Add multi-channel intake adapters for email and portal events.
- Add notifications to staff and patients.
- Add authentication and role-based access.
- Add a proper automation layer using n8n or a similar integration tool.
- Add richer analytics and monitoring.
