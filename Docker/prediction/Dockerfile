FROM python:3.10-slim

WORKDIR /app

# Установим системные зависимости и драйвер SQL Server
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
    libgssapi-krb5-2 \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Добавим репозиторий Microsoft и установим ODBC-драйвер
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

CMD ["python", "block_prediction_bot.py"]
