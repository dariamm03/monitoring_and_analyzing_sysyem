import pickle
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
import xgboost as xgb

app = FastAPI()

# Загружаем модель и векторизатор
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("tfidf.pkl", "rb") as f:
    vectorizer = pickle.load(f)

class LogEntry(BaseModel):
    text: str
    user: str
    process: str
    level: str
    timestamp: str

@app.post("/predict")
async def predict(logs: List[LogEntry]):
    predictions = []

    for log in logs:
        # Трансформируем текст через обученный векторизатор
        text_features = vectorizer.transform([log.text])
        # Преобразуем в DataFrame с правильными названиями фич
        features = pd.DataFrame(text_features.toarray(), columns=vectorizer.get_feature_names_out())

        # Предсказание вероятности
        prob = model.predict_proba(features)[0][1]

        # Пока для примера фичи не извлекаем
        predictions.append({
            "error_probability": prob,
            "likely_user": log.user,
            "likely_process": log.process,
            "top_features": []
        })

    return {"predictions": predictions}
