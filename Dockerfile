# Docker-image til REST API'et. Bygges af docker-compose.yml og af CI.
# Et image er en "pakket" udgave af programmet med Python og alle pakker,
# så det kører ens på PC'en, på GitHub og hos censor.

# Start fra et lille officielt Python-image (slim = uden unødige værktøjer).
FROM python:3.12-slim
# Alle følgende kommandoer kører i mappen /app inde i containeren.
WORKDIR /app
# Kopiér først kun pakkelisten og installér. Docker gemmer dette lag, så pakkerne
# ikke skal installeres igen, når vi kun ændrer i koden (hurtigere builds).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Kopiér selve koden: de tre serverfiler og kontrolcentret.
COPY main.py rules.py db.py ./
COPY static ./static
# Kør ikke som root i containeren (sikkerhed: et angreb får færre rettigheder).
RUN useradd --create-home appuser
USER appuser
# API'et lytter på port 8000.
EXPOSE 8000
# Start-kommando. --host 0.0.0.0 gør API'et tilgængeligt udefra (fra Pi'en), ikke kun lokalt.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
