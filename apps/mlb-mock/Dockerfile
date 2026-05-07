FROM python:3.12-slim

WORKDIR /app
COPY app ./app

EXPOSE 8090
CMD ["python", "app/main.py", "--host", "0.0.0.0", "--port", "8090", "--replay-speed", "300"]
