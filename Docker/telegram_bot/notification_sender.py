# Новый notification_sender.py

import os
import time
import json
import glob
import pandas as pd
import requests
import asyncio
import logging
from telegram import Bot

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PREDICTOR_URL = "http://predictor_service:8000/predict"
LOGS_FILE = os.getenv("LOGS_FILE", "/app/logs.csv")
SETTINGS_DIR = "/app/settings"

bot = Bot(token=TELEGRAM_TOKEN)

async def send_prediction(chat_id, user_name, log_time, message_text):
    text = (
        "⚠️ Обнаружена проблема!\n"
        f"👤 **Пользователь**: `{user_name}`\n"
        f"🕒 **Время**: `{log_time}`\n"
        f"📝 **Ошибка**: `{message_text}`"
    )
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

async def send_notification(chat_id, prediction):
    text = (
        f"🔥 Обнаружена вероятность ошибки ({round(prediction['error_probability']*100)}%)\n"
        f"👤 Пользователь: {prediction['likely_user']}\n"
        f"⚙️ Процесс: {prediction['likely_process']}\n"
        f"📊 Причины: {', '.join(prediction['top_features'])}"
    )
    await bot.send_message(chat_id=chat_id, text=text)
    
async def predict(messages, usernames, times):
    try:
        logs_input = []
        for msg, user, time in zip(messages, usernames, times):
            logs_input.append({
                "text": msg,
                "user": user,
                "process": "backend",  # или другой тег, если есть
                "level": "ERROR",      # можно подставить из логов, если есть
                "timestamp": time
            })

        response = requests.post(PREDICTOR_URL, json=logs_input)

        if response.status_code == 200:
            return response.json()["predictions"]
        else:
            logging.error(f"Predictor service returned {response.status_code}: {response.text}")
            return [0.0] * len(messages)
    except Exception as e:
        logging.error(f"Prediction request failed: {e}")
        return [0.0] * len(messages)

async def main_loop():
    last_sent = {}

    while True:
        if not os.path.exists(LOGS_FILE):
            logging.warning("Logs file not found. Waiting...")
            await asyncio.sleep(10)
            continue

        df = pd.read_csv(LOGS_FILE, delimiter=";").tail(500)  # Только последние 500 строк
        messages = df["FormattedMessage"].fillna(df["Message"]).fillna("").tolist()
        usernames = df["UserName"].fillna("unknown").tolist()
        times = df.iloc[:, 6].fillna("unknown").tolist()  # Дата-время

        preds = await predict(messages)
        print("Результат предсказания:")
        print(preds[:3])  # Покажет первые 3 результата


        for settings_file in glob.glob(f"{SETTINGS_DIR}/*.json"):
            user_id = os.path.basename(settings_file).replace(".json", "")
            with open(settings_file, "r") as f:
                settings = json.load(f)

            threshold = settings.get("threshold", 0.8)
            interval = settings.get("notification_interval", 300)
            last_time = last_sent.get(user_id, 0)
            now = time.time()

            if now - last_time < interval:
                continue  # Пропускаем, если не пришло время слать снова

            for i, pred in enumerate(preds):
                if isinstance(pred, dict):
                    probability = pred.get("error_probability", 0)
                    if probability >= threshold:
                        await send_notification(user_id, pred)
                        last_sent[user_id] = now
                        break  # Только одно сообщение в интервале
                else:
                    continue

        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main_loop())
