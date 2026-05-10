FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/api ./apps/api
COPY packages ./packages
COPY apps/__init__.py ./apps/__init__.py
ENV PYTHONPATH=/app
EXPOSE 18000
CMD ["uvicorn", "apps.api.app.main:app", "--host", "0.0.0.0", "--port", "18000"]
