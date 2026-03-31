from prompt import SYSTEM
import pandas as pd
from utils import send_messasge, ModelMessageDict
from t_minus_generator import generate_t_minus, extract_csv
import pandas as pd

# Загрузка данных
tagged_df = pd.read_excel('batchs/S_p_m.xlsx')
found_df  = pd.read_excel('batchs/found_evidence.xlsx')
found_ids = set(found_df['id'])
model_df  = tagged_df[~tagged_df['id'].isin(found_ids)].reset_index(drop=True)
print(f"Для модели: {len(model_df)} строк")
# Загружаем один problematic пример
row = model_df[model_df['id'] == 5].iloc[0]  # или 71, 76, 93
tbl = pd.read_csv(f"data/{row['context']}", quotechar='"', on_bad_lines='skip', engine='python')

# Формируем запрос
msg = ModelMessageDict(role='user')
msg.add_text_content(
    f"QUESTION: {row['utterance']}\nANSWER: {row['targetValue']}\nTABLE:\n{tbl.head(20).to_csv(index=False)}\nOUTPUT:"
)

# Отправляем и печатаем сырой ответ
success, responses = send_messasge(
    messages=[{"role": "system", "content": SYSTEM}, msg],
    base_url="http://localhost:8880/v1",
    api_key='EMPTY',
    model_name='Qwen/Qwen3-VL-32B-Thinking',
    temperature=0.3,
)

if success:
    print("="*60)
    print("СЫРОЙ ОТВЕТ МОДЕЛИ:")
    print("="*60)
    print(responses[0])
else:
    print(f"Ошибка: {responses}")