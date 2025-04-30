from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
import logging

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

@app.route('/alert', methods=['POST'])
def handle_alert():
    try:
        # Проверка Content-Type
        if not request.is_json:
            logger.error("Invalid Content-Type")
            return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data:
            logger.error("Empty request body")
            return jsonify({"status": "error", "message": "Empty JSON received"}), 400

        # Валидация формата Alertmanager
        if 'alerts' not in data:
            logger.error("Missing 'alerts' field")
            return jsonify({"status": "error", "message": "Invalid Alertmanager payload"}), 400

        message = format_alertmanager_alert(data)
        if not message:
            return jsonify({"status": "error", "message": "No valid alerts to process"}), 400

        send_to_telegram(message)
        return jsonify({"status": "success"})

    except Exception as e:
        logger.exception("Error processing alert")
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/')
def home():
    return "Telegram Alert Bot is running!", 200

@app.route('/log', methods=['POST'])
def handle_log():
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 400

        log_data = request.get_json()
        if not log_data:
            return jsonify({"status": "error", "message": "Empty log data received"}), 400

        message = format_promtail_log(log_data)
        send_to_telegram(message)
        return jsonify({"status": "success"})

    except Exception as e:
        logger.exception("Error processing log")
        return jsonify({"status": "error", "message": str(e)}), 500

def format_alertmanager_alert(alert_data):
    try:
        alerts = alert_data.get('alerts', [])
        if not alerts:
            logger.warning("Empty alerts array")
            return None

        message = "🚨 *Alert Manager Notification*\n"
        for alert in alerts:
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})

            message += (
                f"\n🔹 *Status*: {alert.get('status', 'unknown').upper()}\n"
                f"📛 *Alert*: {labels.get('alertname', 'N/A')}\n"
                f"🔺 *Severity*: {labels.get('severity', 'N/A')}\n"
                f"📝 *Summary*: {annotations.get('summary', 'N/A')}\n"
                f"⏱ *Fired at*: {alert.get('startsAt', 'N/A')}\n"
                f"🔚 *Ended at*: {alert.get('endsAt', 'N/A')}\n"
            )
        return message

    except Exception as e:
        logger.error(f"Formatting error: {str(e)}")
        return None

def format_promtail_log(log_data):
    try:
        streams = log_data.get('streams', [])
        if not streams:
            return "📭 Empty log stream received"

        message = "📋 *New Log Entry*\n"
        for stream in streams[:3]:  # Ограничим 3 потока для избежания спама
            labels = stream.get('labels', {})
            for entry in stream.get('entries', [])[:5]:  # Максимум 5 записей
                timestamp = int(entry['timestamp'][:10]) if entry.get('timestamp') else None
                time_str = datetime.fromtimestamp(timestamp).isoformat() if timestamp else "N/A"
                
                message += (
                    f"\n⏰ *Time*: {time_str}\n"
                    f"🏷 *Labels*: `{labels}`\n"
                    f"📜 *Message*:\n`{entry.get('line', 'empty')}`\n"
                )
        return message

    except Exception as e:
        logger.error(f"Log formatting error: {str(e)}")
        return "⚠️ Error formatting log entry"

def send_to_telegram(text):
    try:
        if not text or not isinstance(text, str):
            raise ValueError("Invalid message text")

        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                'chat_id': CHAT_ID,
                'text': text,
                'parse_mode': 'Markdown',
                'disable_notification': False
            },
            timeout=10
        )
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected Telegram error: {str(e)}")
        raise

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)