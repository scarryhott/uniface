FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml AUTONOMOUS_RUNTIME.md ./
COPY closure_supernet ./closure_supernet
RUN pip install --no-cache-dir .
RUN mkdir -p /data/inbox
ENV CLOSURE_DB_PATH=/data/closure_supernet.db \
    CLOSURE_INBOX_DIR=/data/inbox \
    CLOSURE_AUTONOMY_ENABLED=true
EXPOSE 8000
CMD ["closure-supernet", "serve", "--host", "0.0.0.0", "--port", "8000"]
