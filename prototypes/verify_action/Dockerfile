FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY prototypes/verify_action/requirements-mcp.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY prototypes/verify_action/ ./

EXPOSE 8000

CMD ["sh", "-c", "uvicorn remote_app:app --host 0.0.0.0 --port ${PORT:-8000}"]
