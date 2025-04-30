import asyncio
import json
import os
import pandas as pd
import requests
from fpdf import FPDF
import matplotlib.pyplot as plt
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from notification_sender import send_notification

# Стейты для ConversationHandler
MAIN_MENU, CHOOSING_SETTING, CHOOSING_THRESHOLD, CHOOSING_INTERVAL = range(4)

# Пути к файлам
SETTINGS_DIR = "/app/settings"
LOGS_FILE = "/app/logs/logs.csv"

# Глобальные переменные
TEST_MODE = True
SENT_TEST = False
REPORT_MODE = "last_10"

# -------------- Основные функции --------------

async def send_to_predictor(log_entry):
    url = "http://ml:8000/predict"
    payload = log_entry
    response = requests.post(url, json=payload)
    return response.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update)
    return MAIN_MENU

async def show_main_menu(update: Update):
    buttons = [
    [KeyboardButton("📋 Показать текущие настройки")],
    [KeyboardButton("🛠️ Настроить уведомления")],
    [KeyboardButton("📋 Получить отчет")]
]

    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("👋 Добро пожаловать! Что хотите сделать?", reply_markup=markup)

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📋 Показать текущие настройки":  # тут исправили!
        await show_settings(update)
        return MAIN_MENU
    elif text == "🛠️ Настроить уведомления":
        await ask_setting_choice(update)
        return CHOOSING_SETTING
    elif text == "📋 Получить отчет":   # тут тоже исправь! 📋, а не 📋
        await ask_report_format(update)
        return MAIN_MENU
    else:
        await update.message.reply_text("❗ Пожалуйста, выберите действие с кнопок 👆")
        return MAIN_MENU


async def ask_report_format(update: Update):
    buttons = [
        [KeyboardButton("📃 Excel-отчет")],
        [KeyboardButton("📄 PDF-отчет")],
        [KeyboardButton("🔙 Назад в меню")]
    ]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Выберите формат отчета:", reply_markup=markup)

async def report_format_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📃 Excel-отчет":
        await send_excel_report(update, context)
    elif text == "📄 PDF-отчет":
        await send_pdf_report(update, context)
    elif text == "🔙 Назад в меню":
        await show_main_menu(update)

async def show_settings(update: Update):
    user_id = str(update.effective_user.id)
    settings = load_user_settings(user_id)
    await update.message.reply_text(
        f"📋 Ваши настройки:\n"
        f"• Порог ошибки: {settings['threshold']}\n"
        f"• Интервал уведомлений: {settings['notification_interval']} сек"
    )

# -------------- Отчеты --------------

async def send_excel_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        df = pd.read_csv(LOGS_FILE, sep=';', encoding='utf-8')

        if REPORT_MODE == "last_10":
            df = df.head(10)
        elif REPORT_MODE == "day":
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            last_day = pd.Timestamp.now() - pd.Timedelta(days=1)
            df = df[df['Timestamp'] >= last_day]

        summary_by_category = df.groupby('Category').size().reset_index(name='Count')
        summary_by_severity = df.groupby('Severity').size().reset_index(name='Count')
        top_users = df.groupby('UserName').size().reset_index(name='Logs').sort_values('Logs', ascending=False).head(5)
        top_processes = df.groupby('ProcessName').size().reset_index(name='Logs').sort_values('Logs', ascending=False).head(5)

        if 'Timestamp' in df.columns and not df['Timestamp'].isnull().all():
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            df = df.dropna(subset=['Timestamp'])
            activity_by_day = df['Timestamp'].dt.date.value_counts().reset_index()
            activity_by_day.columns = ['ActivityDate', 'Logs']
            activity_by_day = activity_by_day.sort_values('ActivityDate')
        else:
            activity_by_day = pd.DataFrame(columns=['ActivityDate', 'Logs'])

        report_path = "/app/report.xlsx"
        with pd.ExcelWriter(report_path) as writer:
            df.to_excel(writer, sheet_name="Логи", index=False)
            summary_by_category.to_excel(writer, sheet_name="Категории событий", index=False)
            summary_by_severity.to_excel(writer, sheet_name="Степени серьезности", index=False)
            top_users.to_excel(writer, sheet_name="Топ пользователей", index=False)
            top_processes.to_excel(writer, sheet_name="Топ процессов", index=False)
            activity_by_day.to_excel(writer, sheet_name="Активность по дням", index=False)

        with open(report_path, "rb") as f:
            await update.message.reply_document(document=InputFile(f, filename="report.xlsx"))

        await update.message.reply_text("📋 Excel-отчет успешно создан и отправлен! 🎉")
    except Exception as e:
        await update.message.reply_text(f"❗ Ошибка при создании Excel-отчета: {e}")

async def send_pdf_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        df = pd.read_csv(LOGS_FILE, sep=';', encoding='utf-8')
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df = df.dropna(subset=['Timestamp'])

        top_users = df['UserName'].value_counts().head(5)
        top_processes = df['ProcessName'].value_counts().head(5)
        activity_by_day = df['Timestamp'].dt.date.value_counts().sort_index()

        # Создание графика активности
        plt.figure(figsize=(10, 5))
        activity_by_day.plot(kind='line', marker='o')
        plt.title('Активность по дням')
        plt.xlabel('Дата')
        plt.ylabel('Количество событий')
        plt.grid(True)
        plt.tight_layout()
        graph_path = '/app/activity_graph.png'
        plt.savefig(graph_path)
        plt.close()

        pdf = FPDF()
        pdf.add_page()

        # Добавляем поддержку Юникода (обязательно указать правильный путь к файлу шрифта!)
        pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 16)

        pdf.cell(0, 10, 'Аналитический отчет по логам', ln=True, align='C')

        pdf.ln(10)
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 10, 'Топ пользователей по количеству ошибок:', ln=True)
        for user, count in top_users.items():
            print(f"👤 Проверяем пользователя: {user}")
            pdf.cell(0, 10, f" - {user}: {count}", ln=True)

        pdf.ln(5)
        pdf.cell(0, 10, 'Топ процессов по количеству ошибок:', ln=True)
        for proc, count in top_processes.items():
            pdf.cell(0, 10, f" - {proc}: {count}", ln=True)

        pdf.ln(10)
        pdf.cell(0, 10, 'График активности по дням:', ln=True)
        pdf.image(graph_path, w=180)

        pdf_output = '/app/report.pdf'
        pdf.output(pdf_output)

        with open(pdf_output, "rb") as f:
            await update.message.reply_document(document=InputFile(f, filename="report.pdf"))

        await update.message.reply_text("📄 PDF-отчет успешно создан и отправлен! 🎉")

    except Exception as e:
        await update.message.reply_text(f"❗ Ошибка при создании PDF-отчета: {e}")


# -------------- Работа с настройками пользователей --------------

def save_user_settings(user_id, settings):
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    with open(f"{SETTINGS_DIR}/{user_id}.json", "w") as f:
        json.dump(settings, f, indent=4)

def load_user_settings(user_id):
    filepath = f"{SETTINGS_DIR}/{user_id}.json"
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        # Значения по умолчанию
        default_settings = {
            "threshold": 0.8,
            "notification_interval": 300,
            "chat_id": int(user_id)
        }
        save_user_settings(user_id, default_settings)
        return default_settings


# -------------- Настройка уведомлений (смена порогов и интервалов) --------------

async def ask_setting_choice(update: Update):
    buttons = [
        [KeyboardButton("✏️ Изменить порог ошибки")],
        [KeyboardButton("🕒 Изменить интервал уведомлений")],
        [KeyboardButton("🔙 Назад в меню")]
    ]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Что хотите изменить? 🛠️", reply_markup=markup)

async def setting_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "✏️ Изменить порог ошибки":
        buttons = [
            [KeyboardButton("0.5"), KeyboardButton("0.6")],
            [KeyboardButton("0.7"), KeyboardButton("0.8")],
            [KeyboardButton("0.9")],
            [KeyboardButton("🔙 Назад в меню")]
        ]
        markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        await update.message.reply_text("Выберите новый порог ошибки:", reply_markup=markup)
        return CHOOSING_THRESHOLD
    elif text == "🕒 Изменить интервал уведомлений":
        buttons = [
            [KeyboardButton("60"), KeyboardButton("300")],
            [KeyboardButton("600"), KeyboardButton("1800")],
            [KeyboardButton("🔙 Назад в меню")]
        ]
        markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        await update.message.reply_text("Выберите интервал уведомлений (в секундах):", reply_markup=markup)
        return CHOOSING_INTERVAL
    elif text == "🔙 Назад в меню":
        await show_main_menu(update)
        return MAIN_MENU

async def threshold_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Назад в меню":
        await show_main_menu(update)
        return MAIN_MENU
    try:
        threshold = float(text)
        user_id = str(update.effective_user.id)
        settings = load_user_settings(user_id)
        settings["threshold"] = threshold
        save_user_settings(user_id, settings)
        await update.message.reply_text(f"✅ Порог ошибки установлен на {threshold}")
        await show_main_menu(update)
        return MAIN_MENU
    except ValueError:
        await update.message.reply_text("❗ Выберите значение с кнопок!")
        return CHOOSING_THRESHOLD

async def interval_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Назад в меню":
        await show_main_menu(update)
        return MAIN_MENU
    try:
        interval = int(text)
        user_id = str(update.effective_user.id)
        settings = load_user_settings(user_id)
        settings["notification_interval"] = interval
        save_user_settings(user_id, settings)
        await update.message.reply_text(f"✅ Интервал уведомлений установлен на {interval} сек")
        await show_main_menu(update)
        return MAIN_MENU
    except ValueError:
        await update.message.reply_text("❗ Выберите значение с кнопок!")
        return CHOOSING_INTERVAL

# -------------- Фоновая проверка событий --------------
print("⚡ Запуск процесса опроса пользователей...")

async def polling_loop():
    global TEST_MODE, SENT_TEST
    while True:
        if not TEST_MODE or SENT_TEST:
            await asyncio.sleep(10)
            continue

        settings_files = os.listdir(SETTINGS_DIR)
        for settings_file in settings_files:
            with open(os.path.join(SETTINGS_DIR, settings_file), 'r') as f:
                user_settings = json.load(f)
                chat_id = user_settings.get("chat_id")
                if not chat_id:
                    continue

                test_log = {
                    "text": "Ошибка соединения с базой данных",
                    "user": str(chat_id),
                    "process": "db_connector",
                    "level": "ERROR",
                    "timestamp": "2025-04-27 16:00:00"
                }
                prediction = await send_to_predictor(test_log)
                print(f"📈 Предсказание для пользователя {chat_id}: {prediction}")

                threshold = user_settings.get("threshold", 0.7)
                print(f"🔎 Порог пользователя {chat_id}: {threshold}")
                print(f"🧪 prediction = {prediction}")
                print(f"🧪 threshold = {threshold}")


                if prediction['error_probability'] >= threshold:
                    await send_notification(chat_id, prediction)
                    print(f"✉️ Отправка уведомления пользователю {chat_id}")

                    SENT_TEST = True

        await asyncio.sleep(10)

# -------------- Точка входа --------------

def main():
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        MAIN_MENU: [
            MessageHandler(filters.Regex('^(📋 Показать текущие настройки|🛠️ Настроить уведомления|📋 Получить отчет)$'), main_menu_handler),
            MessageHandler(filters.Regex('^(📃 Excel-отчет|📄 PDF-отчет|🔙 Назад в меню)$'), report_format_handler),
        ],

        CHOOSING_SETTING: [MessageHandler(filters.TEXT & ~filters.COMMAND, setting_choice_handler)],
        CHOOSING_THRESHOLD: [MessageHandler(filters.TEXT & ~filters.COMMAND, threshold_chosen)],
        CHOOSING_INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, interval_chosen)],
    },
    fallbacks=[CommandHandler('start', start)],
)
    application.add_handler(conv_handler)


    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(polling_loop())
    application.run_polling()

if __name__ == "__main__":
    main()
