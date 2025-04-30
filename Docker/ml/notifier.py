import requests
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # читается из переменных окружения

def send_alert_to(chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    return response.ok


# старый вариант, если надо "всем" — можно удалить или оставить как псевдоним
CHAT_ID = os.environ.get("CHAT_ID")  # по умолчанию
def send_alert(message: str):
    if CHAT_ID:
        return send_alert_to(CHAT_ID, message)
    return False
