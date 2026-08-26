FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CLOSURE_DB_PATH=/data/closure_supernet.db \
    CLOSURE_INBOX_DIR=/data/inbox \
    CLOSURE_BACKUP_DIR=/data/backups

RUN addgroup --system closure && adduser --system --ingroup closure --home /app closure

COPY pyproject.toml AUTONOMOUS_RUNTIME.md ./
COPY closure_supernet ./closure_supernet
RUN pip install --no-cache-dir .

RUN mkdir -p /data/inbox /data/backups && chown -R closure:closure /app /data
USER closure

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/livez', timeout=3)"

CMD ["sh", "-c", "closure-supernet serve --host 0.0.0.0 --port ${PORT:-8000}"]
