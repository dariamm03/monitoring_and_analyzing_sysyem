import matplotlib.pyplot as plt

# Названия моделей и их F1-оценки
models = ['RandomForest', 'LogisticRegression', 'GradientBoosting', 'XGBoost']
f1_scores = [0.9992, 0.9942, 0.9996, 0.9998]

# Построение графика
plt.figure(figsize=(10, 6))
bars = plt.bar(models, f1_scores)

# Подписываем значения над столбцами
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.0002, f'{yval:.4f}', ha='center', va='bottom')

plt.title('Сравнение моделей по F1-score')
plt.ylabel('F1-score')
plt.ylim(0.99, 1.001)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
