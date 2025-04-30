FROM python:3.10-slim
WORKDIR /app
COPY app_polling.py .
RUN pip install --no-cache-dir python-telegram-bot requests pandas openpyxl fpdf matplotlib
RUN apt-get update && apt-get install -y fonts-dejavu
CMD ["python", "app_polling.py"]
