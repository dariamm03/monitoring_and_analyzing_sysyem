import pandas as pd
import xgboost as xgb
import pickle
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.utils.class_weight import compute_sample_weight
import matplotlib.pyplot as plt

# === Загрузка датасета ===
df = pd.read_csv("combined_training_dataset.csv")
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# === Удаляем ненужные столбцы ===
X = df.drop(columns=["label", "query", "session_id", "db", "prob"], errors="ignore")
y = df["label"]

# === Деление на train/test ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# === Взвешивание классов для дисбаланса ===
sample_weights = compute_sample_weight("balanced", y_train)

# === Модель и гиперпараметры ===
params = {
    "max_depth": [3, 5, 7],
    "n_estimators": [50, 100],
    "learning_rate": [0.05, 0.1],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0],
}

xgb_clf = xgb.XGBClassifier(
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42
)

# === Поиск лучших параметров ===
grid = GridSearchCV(
    xgb_clf,
    param_grid=params,
    scoring="roc_auc",
    cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
    n_jobs=-1,
    verbose=2
)

print("🔍 Поиск лучших параметров...")
grid.fit(X_train, y_train, sample_weight=sample_weights)
best_model = grid.best_estimator_

# === Оценка ===
y_pred = best_model.predict(X_test)
y_proba = best_model.predict_proba(X_test)[:, 1]

print("\n✅ Лучшие параметры:")
print(grid.best_params_)

print("\n📊 Классификационный отчёт:")
print(classification_report(y_test, y_pred))

print(f"ROC AUC: {roc_auc_score(y_test, y_proba):.4f}")

# === Визуализация важности признаков ===
xgb.plot_importance(best_model, max_num_features=15)
plt.title("Feature Importance")
plt.tight_layout()
plt.savefig("feature_importance.png")
plt.show()

# === Сохранение модели ===
# === Сохранение модели в переносимом JSON-формате ===
best_model.get_booster().save_model("xgb_model.json")
print("💾 JSON-модель сохранена: xgb_model.json")

