FROM python:3.11.8-slim

RUN addgroup --system --gid 1001 appuser \
    && adduser --system --uid 1001 --ingroup appuser appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
