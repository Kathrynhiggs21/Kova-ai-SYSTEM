# Kova AI System - Dockerfile
# Save this as: kova-ai/Dockerfile

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 kova && chown -R kova:kova /app

# Copy requirements first for better caching
COPY --chown=kova:kova requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_lg

# Copy application code
COPY --chown=kova:kova . .

# Switch to non-root user
USER kova

# Production stage
FROM base as production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM base as development
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=development

# Install development dependencies
USER root
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    isort \
    ipython \
    ipdb

USER kova

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]