import requests
import json
import os
import re
import time
from datetime import datetime
import hashlib
import traceback
import pyodbc
import numpy as np
from xgboost import Booster
import xgboost as xgb
from pathlib import Path

# === НАСТРОЙКИ ===
SQLSERVER_CONN = os.getenv("SQLSERVER_CONN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Путь к settings — прямо в контейнере
SETTINGS_DIR = os.getenv("SETTINGS_DIR", "/app/settings")

print("[DEBUG] SCRIPT_DIR:", SCRIPT_DIR)
print("[DEBUG] SETTINGS_DIR:", SETTINGS_DIR)
print("[DEBUG] Файлы:", os.listdir(SETTINGS_DIR) if os.path.exists(SETTINGS_DIR) else "❌ Папка не найдена")



GRAFANA_PLUGIN_PUBLIC = os.path.abspath(
    os.path.join(SCRIPT_DIR, "../Grafana/plugins/grafana-block-alert-panel/public")
)
QUERY_LOG_PATH = "queries.jsonl"
TEXT_LOG_PATH = "logs/queries.log"
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", 0.8))
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(SCRIPT_DIR, "xgb_model.json"))
BLOCK_LOG_PATH = os.path.join(SCRIPT_DIR, "logs", "block_prediction.log")

# === Лог для Grafana Loki ===
def log_for_grafana(prob: float, session_id: str, db: str, sql: str):
    try:
        os.makedirs(os.path.dirname(BLOCK_LOG_PATH), exist_ok=True)
        sql_clean = re.sub(r"\s+", " ", sql.strip())
        line = f"[{datetime.now().isoformat()}] session={session_id} db={db} SQL: {sql_clean} Probability: {prob:.3f}"
        with open(BLOCK_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print("[GRAFANA-LOG]", line)
    except Exception as e:
        print(f"[ERROR] Не удалось записать лог для Grafana: {e}")

# === Фильтр игнорируемых запросов ===
IGNORED_SQL_PATTERNS = [
    r"sys\.dm_exec_",
    r"msrepl_",
    r"sp_ms",
    r"from sys\.dm_exec_requests",
    r"create procedure sys\.sp_msget_repl_commands"
]

def should_ignore_sql(sql: str) -> bool:
    sql = sql.lower()
    return any(re.search(pat, sql) for pat in IGNORED_SQL_PATTERNS)

# === Логика модели ===
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Модель не найдена по пути: {MODEL_PATH}")

model = Booster()
model.load_model(MODEL_PATH)

def extract_features(sql: str, duration: float = 0.0):
    sql = sql.lower()
    temp_tables = re.findall(r"#\w+", sql)
    temp_table_count = len(set(temp_tables))
    complex_join = any(k in sql for k in [" like ", "substring", "charindex", "concat", "trim"])
    return {
        "query_type_encoded": int(0 if "select" in sql else 1 if "update" in sql else 2 if "insert" in sql else 3 if "delete" in sql else 4 if "alter" in sql else 5 if "exec" in sql else 6),
        "has_transaction": int("begin transaction" in sql or "begin tran" in sql),
        "has_join_count": sql.count(" join "),
        "has_subquery": int(sql.count("select") > 1),
        "has_nolock": int("with (nolock)" in sql),
        "has_or_in_where": int(" or " in sql and "where" in sql),
        "uses_temp_table": int("#temp" in sql or "into #" in sql),
        "temp_table_count": temp_table_count,
        "is_ddl": int("alter table" in sql or "drop table" in sql),
        "starts_with_exec": int(sql.strip().startswith("exec")),
        "text_length": len(sql),
        "estimated_rows": min(len(sql) * 10, 100000),
        "complex_join": int(complex_join),
        "query_duration": duration,
        "starts_with_select": int(sql.strip().startswith("select"))
    }

# === Логика логирования и уведомлений ===
def log_query(query: str, session_id: str, db: str = "unknown"):
    os.makedirs(os.path.join(SCRIPT_DIR, "logs"), exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(),
        "query_hash": hashlib.md5(query.encode()).hexdigest(),
        "session_id": session_id,
        "database": db,
        "query": query
    }
    with open(os.path.join(SCRIPT_DIR, QUERY_LOG_PATH), "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def already_logged(session_id: str, query: str):
    path = os.path.join(SCRIPT_DIR, QUERY_LOG_PATH)
    if not os.path.exists(path):
        return False
    query_hash = hashlib.md5(query.encode()).hexdigest()
    with open(path, "r", encoding="utf-8") as f:
        for line in reversed(list(f)):
            try:
                entry = json.loads(line)
                if entry["session_id"] == session_id and entry["query_hash"] == query_hash:
                    return True
            except Exception:
                continue
    return False

def log_query_text_to_file(query: str, session_id: str, db: str = "unknown"):
    with open(os.path.join(SCRIPT_DIR, TEXT_LOG_PATH), "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] session_id={session_id} db={db} sql={query.strip()}\n")

def write_json_log(prob: float, session_id: str, db: str, sql: str):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": session_id,
        "app": db,
        "message": sql.strip(),
        "probability": prob
    }
    path = os.path.join(GRAFANA_PLUGIN_PUBLIC, "logs.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        existing = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        existing.append(log_entry)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(existing[-100:], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] write_json_log: {e}")

def get_chat_ids():
    """Получаем список chat_id из файлов настроек в SETTINGS_DIR"""
    chat_ids = set()
    
    if not os.path.exists(SETTINGS_DIR):
        print(f"[WARNING] Директория с настройками не найдена: {SETTINGS_DIR}")
        return chat_ids
    
    for file in Path(SETTINGS_DIR).glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Предполагаем, что chat_id - это имя файла без расширения
                chat_id = file.stem
                chat_ids.add(chat_id)
        except Exception as e:
            print(f"[ERROR] Ошибка чтения файла настроек {file}: {e}")
    
    print(f"[INFO] Найдено chat_ids: {chat_ids}")
    return chat_ids

def send_telegram_alert(message: str, chat_ids=None):
    if not TELEGRAM_TOKEN:
        print("[WARNING] TELEGRAM_TOKEN не установлен, пропускаем отправку")
        return
    
    if chat_ids is None:
        chat_ids = get_chat_ids()
    
    if not chat_ids:
        print("[WARNING] Не найдено chat_ids для отправки сообщений")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    for chat_id in chat_ids:
        try:
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload)
            
            if not response.ok:
                print(f"[ERROR] Telegram response for chat_id {chat_id}: {response.status_code} — {response.text}")
            else:
                print(f"[INFO] Сообщение отправлено в chat_id {chat_id}")
        except Exception as e:
            print(f"[ERROR] Telegram error for chat_id {chat_id}: {e}")

# === Получение запросов ===
def fetch_active_queries():
    conn = pyodbc.connect(SQLSERVER_CONN)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            r.session_id, 
            DB_NAME(r.database_id) AS db_name, 
            st.text,
            s.program_name,
            r.total_elapsed_time
        FROM sys.dm_exec_requests r
        JOIN sys.dm_exec_sessions s ON r.session_id = s.session_id
        CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) st
        WHERE s.program_name NOT LIKE '%sql-alert-bot%'
    """)
    result = []
    for row in cursor.fetchall():
        sql, session_id, db_name = row.text, str(row.session_id), row.db_name
        elapsed = row.total_elapsed_time or 0
        if sql:
            result.append((sql, session_id, db_name, elapsed / 1000))
    return result

# === Главная функция ===
def check_queries():
    queries = fetch_active_queries()
    print(f"[INFO] Активных запросов: {len(queries)}")

    for sql, session_id, db, duration in queries:
        if should_ignore_sql(sql):
            continue

        print(f"\n[QUERY] session={session_id} db={db}\n{sql.strip()}")

        if not already_logged(session_id, sql):
            log_query(sql, session_id, db)
            log_query_text_to_file(sql, session_id, db)

        features = extract_features(sql, duration)
        dmat = xgb.DMatrix(np.array([[features[k] for k in features]]), feature_names=list(features))

        try:
            prob = model.predict(dmat)[0]
        except Exception as e:
            print(f"[ERROR] predict: {e}")
            continue

        print(f"[DEBUG] Вероятность: {prob:.3f}")
        log_for_grafana(prob, session_id, db, sql)
        write_json_log(prob, session_id, db, sql)

        if prob > ALERT_THRESHOLD:
            msg = (
                "🚨 *Потенциальная блокировка MSSQL*\n"
                f"*Сессия:* `{session_id}`\n"
                f"*База данных:* `{db}`\n"
                f"*Вероятность:* `{prob:.2%}`\n"
                f"*SQL:* `{sql.strip().replace('`', '')[:200]}...`"
            )
            send_telegram_alert(msg)

# === Запуск ===
if __name__ == "__main__":
    print("[INFO] MSSQL-блокировочный бот запущен.")
    try:
        while True:
            check_queries()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[INFO] Бот остановлен вручную.")
    except Exception as e:
        print(f"[ERROR] {e}")
        traceback.print_exc()