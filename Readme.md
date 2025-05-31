## Description

This is a template for a container-based serverless app that answers two user tasks — current weather and time for a city (presently only “New York”). It wraps those tools in a Google ADK agent and exposes a single `/ask` HTTPS endpoint on AWS Lambda.

## Local Testing

Clone, install dependencies, and run app:

```
git clone https://github.com/kadimula/adkTest.git &&
cd adkTest &&
pip install -r requirements.txt &&

brew install ollama &&

ollama pull tinyllama:latest && ollama serve &
uvicorn main:app --reload
```

Test with curl:

```
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in New York?"}'

```

## Structure

```

adkTest/
├── multi_tool_agent/
│ ├── **init**.py # package init
│ └── agent.py # builds the weather_time_agent
├── main.py # FastAPI app + Lambda handler
├── requirements.txt # pinned deps
├── Dockerfile # container recipe
└── .github/workflows/
└── deploy.yml # CI/CD pipeline
```

## FastAPI service layer (`main.py`)

- Starts a **FastAPI** app.
- Instantiates the `weather_time_agent` from `multi_tool_agent.agent`.
- Defines `POST /ask` that receives JSON `{ "city": "...", "task": "weather"|"time" }`, forwards to the agent, and returns its reply.
- Exposes `handler = mangum.Mangum(app)` so the same code runs locally **or** inside Lambda’s event loop.

## Agent layer (`multi_tool_agent/agent.py`)

- Uses **Google ADK 1.1.x** to register two tool functions:
  - `get_weather(city)` – queries an external weather API.
  - `get_time(city)` – returns `datetime.now(tz)` for the city.
- ADK handles argument validation, tool routing, and JSON-serialised records of each call for auditability.

## Containerisation (Dockerfile)

- **Base image** `public.ecr.aws/lambda/python:3.11` keeps it compatible with Lambda’s container runtime.
- `pip install -r requirements.txt` (deps: FastAPI, Mangum, google-adk, boto3, tzdata).
- Copies source code and sets `CMD ["main.handler"]`, so Lambda loads the FastAPI app automatically.

# AWS infrastructure

| Component                  | Role                                                           |
| -------------------------- | -------------------------------------------------------------- |
| **Amazon ECR**             | Stores the built container image.                              |
| **AWS Lambda (container)** | Runs the image on-demand; allocated 512 MB in example logs.    |
| **Lambda Function URL**    | Public HTTPS URL—avoids API Gateway fees; requests hit `/ask`. |
| **IAM role**               | Lets the function read secrets (API keys) & CloudWatch logs.   |

## CI/CD pipeline (`deploy.yml`)

1. **Trigger** – every push to `main`.
2. **Checkout** code.
3. **Configure AWS credentials** via `aws-actions/configure-aws-credentials`.
4. **Log in** to ECR.
5. **docker build --platform linux/amd64 -t $IMAGE_REPO:$SHA …** then `docker push`.
6. **aws lambda update-function-code** to point the function to the new image tag.
7. Optionally runs post-deployment tests (e.g., `curl $FUNCTION_URL/ping`).
   _(Each step is a separate GitHub Actions job step.)_

## Request flow at runtime

User ➜ HTTPS POST /ask ➜ Lambda Function URL
➜ Lambda container spins / re-uses FastAPI app
➜ FastAPI ➜ ADK agent ➜ chosen tool
↩ returns JSON response

pgsql
Copy
Edit

Cold-start latency is minimised by: small base image, Python 3.11 runtime optimisations, and avoiding API Gateway.

## Extensibility & goals

- **Model flexibility** – ADK switches LLMs (e.g., Bedrock → OpenAI) via config only.
- **More tools** – drop new methods into `agent.py`; ADK routes them automatically.
- **Locales** – move the city/time-zone map to a small DynamoDB table or static JSON to widen coverage.
- **Observability** – CloudWatch logs & ADK call records provide traceability; can add AWS X-Ray for traces.

This architecture balances _developer ergonomics_ (FastAPI, Docker) with _deployment economy_ (single Lambda container & Function URL).
