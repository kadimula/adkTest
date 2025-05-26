"""
FastAPI application served via AWS Lambda (container image).

Endpoints
---------
GET  /ping        – liveness check
POST /ask         – { "city": <str>, "task": "weather" | "time" }
"""

from __future__ import annotations

import logging
import os
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from mangum import Mangum

from multi_tool_agent.agent import root_agent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

app = FastAPI(title="ADK multi‑tool demo")
log.info("FastAPI Lambda container starting up…")


class Query(BaseModel):
    city: str = Field(..., min_length=1, description="Target city name")
    task: Literal["weather", "time"]

    # Normalize city names early
    @validator("city")
    def strip_city(cls, v: str) -> str:  # noqa: D401
        return v.strip()


@app.get("/ping", response_model=dict)
def ping() -> dict:  # noqa: D401
    """Simple liveness probe."""
    return {"status": "ok"}


@app.post("/ask", response_model=dict)
def ask(q: Query) -> JSONResponse:
    log.info("User message: %s", q.message)

    try:
        result = root_agent.run(q.message)  # 👈 now the agent decides

        return JSONResponse(
            content={"status": "success", "response": result}, status_code=200
        )

    except Exception as exc:
        log.exception("Agent error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


# When deploying behind Lambda URL the base path is '/default'.
api_base_path = os.getenv("API_BASE_PATH", "/default")

handler = Mangum(app, api_gateway_base_path=api_base_path)
