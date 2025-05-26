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
        result = root_agent.run_tool("get_weather", {"city": q.city})
    elif q.task == "time":
        result = root_agent.run_tool("get_current_time", {"city": q.city})
    else:
        return {"status": "error", "error_message": f"Unknown task '{q.task}'"}

    # Debug print for Lambda logs
    print("Agent result:", result)
    return result


# AWS Lambda entry‑point
handler = Mangum(app)
