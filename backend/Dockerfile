FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

# Установка зависимостей для сборки psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN poetry config virtualenvs.create false \
 && poetry install --no-root

COPY . /app/
