from fastapi import FastAPI, Request
from multi_tool_agent.agent import root_agent
from mangum import Mangum

app = FastAPI()


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/run_tool")
async def run_tool(req: Request):
    body = await req.json()
    tool = body.get("tool")
    args = body.get("args", {})
    result = root_agent.run_tool(tool, args)
    return result


handler = Mangum(app)
