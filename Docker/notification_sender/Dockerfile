FROM python:3.10-slim
WORKDIR /app
COPY notification_sender.py .
RUN pip install pandas requests python-telegram-bot==20.3
CMD ["python", "notification_sender.py"]
