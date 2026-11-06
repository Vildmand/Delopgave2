# Docker-image til REST API'et. Bygges af docker-compose.yml og af CI.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py rules.py db.py ./
COPY static ./static
# Kør ikke som root i containeren (sikkerhed).
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
