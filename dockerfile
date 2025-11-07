cat > Dockerfile << 'EOF'
FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# deps pour compiler spacy et roues manquantes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# dépendances
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt \
 && python -m spacy download fr_core_news_md

# code
COPY app.py /app/app.py

EXPOSE 8010
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8010"]
EOF
