import pandas as pd
import matplotlib.pyplot as plt

# Загрузка датасета
print("\U0001F4C2 Загружаем логи...")
df = pd.read_csv('logs.csv', sep=';')

# Обработка пропусков
print("\u2728 Обрабатываем пропуски...")
df.fillna('', inplace=True)

# Создание целевой переменной IsError
print("\U0001F4C8 Вычисляем целевую переменную IsError...")
df['IsError'] = df['Category'].apply(lambda x: 1 if x in ['WARN', 'ERROR'] else 0)

# Подсчёт количества ошибок и норм
error_counts = df['IsError'].value_counts()

print("\nРаспределение классов:")
print(error_counts)

# Процент ошибок
error_percent = (error_counts[1] / len(df)) * 100
print(f"\n\u26A1 Доля ошибок: {error_percent:.2f}% из всех логов")

# Строим диаграмму
plt.figure(figsize=(6,4))
error_counts.plot(kind='bar', color=['green', 'red'])
plt.title('Распределение ошибок и нормальных логов')
plt.xticks([0,1], ['Норма (0)', 'Ошибка (1)'], rotation=0)
plt.ylabel('Количество логов')
plt.grid(axis='y')
plt.tight_layout()
plt.show()
