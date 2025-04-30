import time
import requests
import os
import json
import joblib
import random
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
SETTINGS_FILE = "/app/user_settings.json"
DEFAULT_SETTINGS = {
    "frequency": 30,
    "threshold": 0.9,
    "muted": False,
    "period": "today"
}

# Загрузка модели
model = joblib.load('/app/model.pkl')

tfidf = joblib.load('/app/tfidf.pkl')

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def send_message(chat_id, text):
    try:
        requests.post(f"{BASE_URL}/sendMessage", data={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"⚠️ Ошибка отправки сообщения в Telegram: {e}")

def get_user_settings(chat_id, settings_data):
    return settings_data.get(chat_id, DEFAULT_SETTINGS)

def predict_log_message(message_text):
    """Предсказываем вероятность ошибки на основе текста лога"""
    try:
        X = tfidf.transform([message_text])
        proba = model.predict_proba(X)[0][1]  # вероятность класса "ошибка"
        return proba
    except Exception as e:
        print(f"⚠️ Ошибка предсказания: {e}")
        return 0

def simulate_new_log():
    """Имитируем поступление нового лог-сообщения для тестов"""
    samples = [
        "Error: Unable to connect to database",
        "User successfully logged in",
        "Warning: Disk space is running low",
        "Unhandled exception in controller",
        "Scheduled job completed without issues",
    ]
    return random.choice(samples)

def main():
    while True:
        settings_data = load_settings()
        new_log = simulate_new_log()
        print(f"📝 Новый лог: {new_log}")

        prediction_score = predict_log_message(new_log)

        for chat_id in settings_data.keys():
            user_settings = get_user_settings(chat_id, settings_data)
            threshold = user_settings.get("threshold", DEFAULT_SETTINGS["threshold"])
            muted = user_settings.get("muted", DEFAULT_SETTINGS["muted"])

            if muted:
                continue

            if prediction_score > threshold:
                text = f"🚨 Обнаружена возможная ошибка:\n{new_log}\nВероятность: {prediction_score:.0%}"
                send_message(chat_id, text)

        time.sleep(5)  # 5 минут пауза между циклами

if __name__ == "__main__":
    main()
