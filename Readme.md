This is a containerized serverless application using FastAPI + Google ADK (Agent Development Kit), deployed to AWS Lambda as a Docker container, with GitHub Actions handling CI/CD.

The purpose of the app is to serve an agent called weather_time_agent, which can answer questions about the current weather and time in a specific city (currently supports only "New York").

The app exposes a FastAPI endpoint /ask that takes a city and task ("weather" or "time") and invokes the correct tool through the ADK agent.

Structure:

adkTest/
├── multi_tool_agent/
│ ├── **init**.py
│ └── agent.py # Defines root_agent with 2 tools: get_weather and get_current_time
├── main.py # FastAPI app that routes to root_agent via Mangum handler
├── requirements.txt # fastapi, mangum, google-adk, boto3, etc.
├── Dockerfile # Uses AWS Lambda base image for Python 3.11
├── .gitignore
└── .github/workflows/deploy.yml # GitHub Actions workflow: builds & pushes to ECR, deploys to Lambda

My goals:

- Keep image size minimal for faster cold starts
- Use AWS Lambda Function URLs (no API Gateway)
- Support Bedrock models and be able switch models easily
