# ---- base image: AWS Lambda runtime for Python 3.11 ----
FROM public.ecr.aws/lambda/python:3.11

# Faster installs & smaller image
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_CACHE_DIR='/tmp'

WORKDIR /var/task

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Set the Lambda handler
CMD ["main.handler"]
