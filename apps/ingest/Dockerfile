FROM python:3.12-slim

WORKDIR /app
COPY apps/ingest /app/apps/ingest
COPY apps/__init__.py /app/apps/__init__.py

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "apps.ingest.app.job"]
