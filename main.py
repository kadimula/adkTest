# main.py
from __future__ import annotations

import asyncio, logging, os, uuid
from fastapi import FastAPI, Request
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types
from mangum import Mangum
from multi_tool_agent.agent import root_agent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger(__name__)

app = FastAPI(title="ADK multi-tool demo")

# ---------- ADK wiring (one-time) ----------
_service = InMemorySessionService()
APP, UID = "weather_time_app", "local-user"
runner = Runner(agent=root_agent, app_name=APP, session_service=_service)
# ------------------------------------------


@app.get("/ping")
def ping() -> dict:
    return {"status": "ok"}


@app.post("/ask")
async def ask(request: Request):
    body = await request.json()
    message: str = body["message"]

    # One session for the whole demo; change to uuid4() per-user if you wish
    session_id = "session"

    # Ensure the session exists (harmless if it already does)
    await _service.create_session(app_name=APP, user_id=UID, session_id=session_id)

    new_message = genai_types.Content(
        role="user",
        parts=[
            genai_types.Part(
                text="You can use the tools 'get_weather(city: str)' and 'get_current_time(city: str)'. "
                "Use them depending on whether the user is asking about weather or time.\n\n"
                + message
            )
        ],
    )

    final_text: str | None = None
    async for event in runner.run_async(
        user_id=UID,
        session_id=session_id,
        new_message=new_message,
    ):
        # The helper marks the agent’s last reply in the turn
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text

    return {"status": "success", "response": final_text or ""}


# Lambda entry-point (works locally too)
handler = Mangum(app, api_gateway_base_path=os.getenv("API_BASE_PATH", "/default"))
