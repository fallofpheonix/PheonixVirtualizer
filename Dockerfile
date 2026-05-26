FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including git for PR analysis)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to allow for self-analysis and access to models/parsers
COPY . .

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PROJECT_ROOT=/app

# Default command runs the CLI Gatekeeper
# Can be overridden to run the FastAPI server: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
ENTRYPOINT ["python", "backend/cli.py"]
CMD ["--path", ".", "--fail-on", "high"]
