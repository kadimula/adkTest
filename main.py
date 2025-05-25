from fastapi import FastAPI
from pydantic import BaseModel
from mangum import Mangum
from multi_tool_agent.agent import root_agent

app = FastAPI()


class Query(BaseModel):
    city: str
    task: str  # "weather" or "time"


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/ask")
def ask(q: Query):
    if q.task == "weather":
        return root_agent.run_tool("get_weather", {"city": q.city})
    return root_agent.run_tool("get_current_time", {"city": q.city})


# AWS Lambda entry‑point
handler = Mangum(app)
