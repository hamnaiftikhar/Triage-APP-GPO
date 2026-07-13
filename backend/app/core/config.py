from __future__ import annotations

from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Telemedicine Triage MVP")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://triage:triage@localhost:5432/triage")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    staff_token: str = os.getenv("STAFF_TOKEN", "triage-staff-secret-token")

    # LangSmith tracing settings
    langchain_tracing_v2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    langchain_endpoint: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    langchain_api_key: str | None = os.getenv("LANGCHAIN_API_KEY")
    langchain_project: str = os.getenv("LANGCHAIN_PROJECT", "telemedicine-triage-mvp")


settings = Settings()
