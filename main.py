# main.py
from __future__ import annotations

import logging, os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types
from mangum import Mangum
from multi_tool_agent.agent import root_agent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger(__name__)

app = FastAPI(title="ADK multi‑tool demo")


class Query(BaseModel):
    message: str


# ADK session + runner wiring (one‑time)
_service = InMemorySessionService()
APP, UID, SID = "weather_time_app", "lambda", "session"
_service.create_session(app_name=APP, user_id=UID, session_id=SID)
runner = Runner(agent=root_agent, app_name=APP, session_service=_service)


@app.get("/ping")
def ping() -> dict:
    return {"status": "ok"}


@app.post("/ask")
def ask(q: Query) -> JSONResponse:
    try:
        content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=q.message)]
        )

        events = runner.run(user_id=UID, session_id=SID, new_message=content)

        responses = [
            e.content.parts[0].text
            for e in events
            if e.content and e.content.parts and e.content.parts[0].text
        ]

        return JSONResponse({"status": "success", "response": "\n\n".join(responses)})

    except Exception as exc:
        log.exception("agent error")
        raise HTTPException(status_code=500, detail="internal server error") from exc


handler = Mangum(app, api_gateway_base_path=os.getenv("API_BASE_PATH", "/default"))
