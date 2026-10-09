# debug_sync.py
from prompt import SYSTEM
import pandas as pd
from utils import send_messasge, ModelMessageDict  # ← синхронная версия

# Загрузка данных

model_df = pd.read_csv('T_m_log/retry_failed_details.csv',sep='\t', encoding='utf-8')
print(f"Для модели: {len(model_df)} строк")

# Загружаем один проблемный пример (поменяйте ID при необходимости)
row = model_df[model_df['id'] == 92].iloc[0]
print(f"🔍 Тестируем id={row['id']}: {row['utterance'][:50]}...")
print(row)
# Читаем таблицу
#tbl = pd.read_csv(f"data/{row['context']}", quotechar='"', on_bad_lines='skip', engine='python')
tbl = pd.read_csv(
    f"data/{row['context']}",
    quotechar='"',
    escapechar='\\',  # Добавляем escape-символ
    engine='python',
    on_bad_lines='skip'
)
tbl_input = tbl.head(30) # Берем первые 20 строк как в запросе

print(f"📊 Таблица: {tbl_input.shape[0]} строк × {tbl_input.shape[1]} колонок")

# ==========================================
# 📋 ВЫВОД ОРИГИНАЛЬНОЙ ТАБЛИЦЫ (ДЛЯ СРАВНЕНИЯ)
# ==========================================
print("\n" + "=" * 60)
print("📊 ОРИГИНАЛЬНАЯ ТАБЛИЦА (входные данные):")
print("=" * 60)
print(tbl_input.to_string(index=False))
print("=" * 60 + "\n")

# Формируем запрос
msg = ModelMessageDict(role='user')
msg.add_text_content(
    f"QUESTION: {row['utterance']}\nANSWER: {row['targetValue']}\nTABLE:\n{tbl_input.to_string(index=False)}\nOUTPUT:"
)

# Отправляем запрос (синхронно)
print("📤 Отправка запроса к модели...")
success, responses = send_messasge(
    messages=[{"role": "system", "content": SYSTEM}, msg],
    base_url="http://192.168.19.127:9886/v1",
    api_key='EMPTY',
    model_name='Qwen/Qwen3-4B-Instruct-2507',
    temperature=0.3,
)

# Вывод результата
if success and responses:
    print("\n" + "=" * 60)
    print("📦 СЫРОЙ ОТВЕТ МОДЕЛИ (T-):")
    print("=" * 60)
    print(responses[0])
    print("=" * 60)

else:
    print(f"\n❌ Ошибка: {responses}")