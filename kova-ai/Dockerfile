FROM python:3.11.8-slim

# Install system dependencies for Python packages (especially psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 1001 appuser \
    && adduser --system --uid 1001 --ingroup appuser appuser

WORKDIR /app

COPY requirements.txt .
# Upgrade pip and install with trusted hosts for better reliability
RUN pip install --upgrade pip && \
    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

# Create a startup command that validates environment before starting the app
CMD ["/bin/bash", "-c", "if [ -f /app/scripts/check_env.sh ]; then /app/scripts/check_env.sh; fi && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
