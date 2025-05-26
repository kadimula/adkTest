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

# --------------------------------------------------------------------------- #
#  Logging
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  FastAPI setup
# --------------------------------------------------------------------------- #
app = FastAPI(title="ADK multi‑tool demo")
log.info("✅ FastAPI Lambda container starting up…")


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
def ask(q: Query) -> JSONResponse:  # noqa: D401
    """Route request to the appropriate ADK tool."""
    log.info("Received task=%s city=%s", q.task, q.city)

    try:
        if q.task == "weather":
            result = root_agent.run_tool("get_weather", {"city": q.city})
        elif q.task == "time":
            result = root_agent.run_tool("get_current_time", {"city": q.city})
        else:  # This branch is unreachable thanks to the Literal type
            raise HTTPException(status_code=400, detail=f"Unknown task '{q.task}'")

        status_code = 200 if result.get("status") == "success" else 400
        return JSONResponse(content=result, status_code=status_code)

    except Exception as exc:  # pylint: disable=broad-except
        log.exception("Unhandled exception processing request: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


# --------------------------------------------------------------------------- #
#  Lambda entry point
# --------------------------------------------------------------------------- #
# If you deploy behind a Lambda URL the base path is '/default'.
# For API Gateway stages use '/prod', '/test', etc.
api_base_path = os.getenv("API_BASE_PATH", "/default")

handler = Mangum(app, api_gateway_base_path=api_base_path)
