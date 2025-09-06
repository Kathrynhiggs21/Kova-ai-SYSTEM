FROM python:3.11-slim as base
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc g++ git curl postgresql-client \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 kova && chown -R kova:kova /app
COPY --chown=kova:kova requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_lg
COPY --chown=kova:kova . .
USER kova

FROM base as production
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 ENVIRONMENT=production
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]

FROM base as development
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 ENVIRONMENT=development
USER root
RUN pip install --no-cache-dir pytest pytest-asyncio pytest-cov black isort ipython ipdb
USER kova
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--reload"]
