FROM python:3.11-slim

# Установка системных зависимостей для SQLite
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости первыми для кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директорию для БД
RUN mkdir -p /app/data

# Переменные окружения по умолчанию
ENV TELEGRAM_TOKEN=default_token
ENV DB_FILE=/app/data/habits.db

CMD ["python", "main.py"]