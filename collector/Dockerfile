FROM python:3.13-slim

WORKDIR /app

COPY collector/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY collector/ ./collector/

ENV PYTHONPATH=/app

CMD ["python", "-m", "collector.main"]
