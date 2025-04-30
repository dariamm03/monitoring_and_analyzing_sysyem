import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack

# Загрузка логов
df = pd.read_csv('logs.csv', sep=';')

# Убираем пропуски
df.fillna('', inplace=True)

# Автоматически создать IsError: если Category == "WARN" или "ERROR" -> 1, иначе 0
df['IsError'] = df['Category'].apply(lambda x: 1 if x in ['WARN', 'ERROR'] else 0)


# Целевая переменная
y = df['IsError']

# Признаки
X_text = df['FormattedMessage']
X_user = df['UserName']
X_proc = df['ProcessName']
X_sev = df['Severity']
X_time = pd.to_datetime(df['Timestamp'], errors='coerce')

# Создаем признаки времени
df['hour'] = X_time.dt.hour.fillna(0).astype(int)
df['weekday'] = X_time.dt.weekday.fillna(0).astype(int)

# Кодируем текст TF-IDF
tfidf = TfidfVectorizer(max_features=500)
X_text_tfidf = tfidf.fit_transform(X_text)

# Кодируем категориальные признаки
enc_user = LabelEncoder()
enc_proc = LabelEncoder()
enc_sev = LabelEncoder()

user_encoded = enc_user.fit_transform(X_user)
proc_encoded = enc_proc.fit_transform(X_proc)
sev_encoded = enc_sev.fit_transform(X_sev)

# Стандартизация мета-признаков
meta_features = pd.DataFrame({
    'user': user_encoded,
    'proc': proc_encoded,
    'sev': sev_encoded,
    'hour': df['hour'],
    'weekday': df['weekday']
})

scaler = StandardScaler()
meta_scaled = scaler.fit_transform(meta_features)

# Объединяем признаки
X_final = hstack([X_text_tfidf, meta_scaled])

# Делим данные
X_train, X_test, y_train, y_test = train_test_split(X_final, y, test_size=0.2, random_state=42)

# Обучаем модель
model = RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42)
model.fit(X_train, y_train)

# Сохраняем всё
joblib.dump(model, 'model.pkl')
joblib.dump(tfidf, 'tfidf.pkl')
joblib.dump(enc_user, 'enc_user.pkl')
joblib.dump(enc_proc, 'enc_proc.pkl')
joblib.dump(enc_sev, 'enc_sev.pkl')
joblib.dump(scaler, 'scaler.pkl')

print("✅ Обучение и сохранение завершено!")
