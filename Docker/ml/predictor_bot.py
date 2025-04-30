import asyncio
import json
import pandas as pd
import telebot
from telebot import types
import joblib
import os
from datetime import datetime

# Загрузка модели и векторизатора
model = joblib.load('model.pkl')
tfidf = joblib.load('tfidf.pkl')

# Инициализация бота
TOKEN = '8105294907:AAGzxwCWn174vlDuYJ6hEZKSM0d6hjkU1qg'
bot = telebot.TeleBot(TOKEN)

# Путь к файлу логов
LOG_FILE = 'logs.csv'
# Путь к файлу настроек пользователей
SETTINGS_FILE = 'user_settings.json'

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "threshold": 0.5,
    "interval": 60,  # секунд между проверками
    "last_log_id": None
}

# Храним настройки в памяти
user_settings = {}

# ==================== Вспомогательные функции ====================

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_settings():
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(user_settings, f, indent=4)

def get_user_settings(user_id):
    if str(user_id) not in user_settings:
        user_settings[str(user_id)] = DEFAULT_SETTINGS.copy()
    return user_settings[str(user_id)]

def get_predictions(texts, threshold):
    X = tfidf.transform(texts)
    probs = model.predict_proba(X)[:, 1]
    results = []
    for i, prob in enumerate(probs):
        if prob >= threshold:
            results.append((texts[i], prob))
    return results

def get_new_logs(last_id):
    try:
        df = pd.read_csv(LOG_FILE, sep=';')
    except Exception as e:
        print(f"Ошибка чтения логов: {e}")
        return pd.DataFrame()

    df = df.fillna('')

    # Просто находим новые записи по индексу
    if last_id is None:
        return df
    else:
        idx = df[df['ThreadId'] == last_id].index
        if not idx.empty:
            return df.iloc[idx[0]+1:]
        else:
            return df
    return df

# ==================== Команды ====================

@bot.message_handler(commands=['start'])
async def start_handler(message):
    user_id = message.from_user.id
    get_user_settings(user_id)
    save_settings()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Изменить порог", callback_data='change_threshold'))
    markup.add(types.InlineKeyboardButton("Изменить интервал", callback_data='change_interval'))
    await bot.send_message(user_id, "👋 Привет! Я бот для уведомлений по логам. Что хочешь изменить?", reply_markup=markup)

# ==================== Обработка кнопок ====================

@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    user_id = call.from_user.id
    if call.data == 'change_threshold':
        await bot.send_message(user_id, "Введите новый порог от 0 до 1:")
        bot.register_next_step_handler_by_chat_id(user_id, process_threshold)
    elif call.data == 'change_interval':
        await bot.send_message(user_id, "Введите новый интервал проверки в секундах:")
        bot.register_next_step_handler_by_chat_id(user_id, process_interval)

async def process_threshold(message):
    user_id = message.from_user.id
    try:
        threshold = float(message.text.strip())
        if 0 <= threshold <= 1:
            user_settings[str(user_id)]['threshold'] = threshold
            save_settings()
            await bot.send_message(user_id, f"✅ Новый порог: {threshold}")
        else:
            await bot.send_message(user_id, "❌ Неверное значение. Введите число от 0 до 1.")
    except ValueError:
        await bot.send_message(user_id, "❌ Ошибка ввода. Введите число от 0 до 1.")

async def process_interval(message):
    user_id = message.from_user.id
    try:
        interval = int(message.text.strip())
        if interval > 0:
            user_settings[str(user_id)]['interval'] = interval
            save_settings()
            await bot.send_message(user_id, f"✅ Новый интервал: {interval} секунд")
        else:
            await bot.send_message(user_id, "❌ Интервал должен быть больше 0.")
    except ValueError:
        await bot.send_message(user_id, "❌ Ошибка ввода. Введите целое число.")

# ==================== Основной цикл ====================

async def check_logs_loop():
    while True:
        for user_id, settings in user_settings.items():
            try:
                interval = settings.get('interval', 60)
                threshold = settings.get('threshold', 0.5)
                last_log_id = settings.get('last_log_id')

                new_logs = get_new_logs(last_log_id)

                if not new_logs.empty:
                    texts = new_logs['FormattedMessage'].astype(str).tolist()
                    preds = get_predictions(texts, threshold)

                    for text, prob in preds:
                        await bot.send_message(user_id, f"⚡ Найдено событие!\n\n{str(text)[:4000]}\n\nВероятность: {prob:.2f}")

                    # Обновляем последний лог
                    new_last_log_id = new_logs.iloc[-1]['ThreadId']
                    user_settings[str(user_id)]['last_log_id'] = new_last_log_id
                    save_settings()

                await asyncio.sleep(interval)
            except Exception as e:
                print(f"Ошибка для пользователя {user_id}: {e}")
                continue

async def main():
    asyncio.create_task(check_logs_loop())
    await bot.polling(non_stop=True)

if __name__ == "__main__":
    user_settings = load_settings()
    asyncio.run(main())
