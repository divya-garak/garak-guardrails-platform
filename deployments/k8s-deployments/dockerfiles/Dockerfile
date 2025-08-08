# Default NeMo Guardrails Dockerfile
FROM python:3.11-slim

LABEL maintainer="NeMo Guardrails Team"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN pip install -e .

EXPOSE 8000

CMD ["python", "-m", "nemoguardrails.server.api", "--host", "0.0.0.0", "--port", "8000"]