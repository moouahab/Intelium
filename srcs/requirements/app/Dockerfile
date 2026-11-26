FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# Scan et OCR, avec les langues configurées dans scraping.yaml.
RUN apt-get update \
    && apt-get install -y --no-install-recommends yara tesseract-ocr tesseract-ocr-eng tesseract-ocr-fra \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . .

# Entrée par défaut : run sans IA (évite de bloquer si la commande IA n'est pas dispo)
CMD ["python", "main.py", "--config", "config/conf.yaml", "--no-ai-report"]
