import pandas as pd
import joblib
from scipy.sparse import hstack

# 📦 Загружаем все пайплайны
model = joblib.load('model.pkl')
tfidf = joblib.load('tfidf.pkl')
enc_user = joblib.load('enc_user.pkl')
enc_proc = joblib.load('enc_proc.pkl')
enc_sev = joblib.load('enc_sev.pkl')
scaler = joblib.load('scaler.pkl')

print("✅ Модель и обработчики загружены")

# 📂 Читаем только 10 строк логов
df = pd.read_csv('logs.csv', sep=';', nrows=10)
df.fillna('', inplace=True)

# 🎯 Извлекаем нужные признаки
X_text = df['FormattedMessage']
X_user = df['UserName']
X_proc = df['ProcessName']
X_sev = df['Severity']
X_time = pd.to_datetime(df['Timestamp'], errors='coerce')

# Временные признаки
df['hour'] = X_time.dt.hour.fillna(0).astype(int)
df['weekday'] = X_time.dt.weekday.fillna(0).astype(int)

# Преобразования
X_text_tfidf = tfidf.transform(X_text)
user_encoded = enc_user.transform(X_user)
proc_encoded = enc_proc.transform(X_proc)
sev_encoded = enc_sev.transform(X_sev)

meta_features = pd.DataFrame({
    'user': user_encoded,
    'proc': proc_encoded,
    'sev': sev_encoded,
    'hour': df['hour'],
    'weekday': df['weekday']
})

meta_scaled = scaler.transform(meta_features)

# Объединяем
X_final = hstack([X_text_tfidf, meta_scaled])

# 🔥 Предсказание
preds_proba = model.predict_proba(X_final)[:, 1]  # вероятность класса 1 (ошибка)

# 🚀 Вывод результата
for i, proba in enumerate(preds_proba):
    print(f"Лог {i+1}: Вероятность ошибки = {proba:.2f}")

print("✅ Предсказание завершено!")
