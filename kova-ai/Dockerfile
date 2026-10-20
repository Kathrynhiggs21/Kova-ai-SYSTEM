FROM python:3.11.8-slim

RUN addgroup --system --gid 1001 appuser \
    && adduser --system --uid 1001 --ingroup appuser appuser

WORKDIR /app/kova-ai

COPY kova-ai/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser kova-ai/app ./app
COPY --chown=appuser:appuser kova_repos_config.json /app/kova_repos_config.json
COPY --chown=appuser:appuser site_final.zip images.zip /app/

# Local compilation/upload needs separate tooling and owner authorization.
ENV KOVA_EXPORT_UPLOAD_ENABLED=false

USER appuser

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
