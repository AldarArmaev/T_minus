from t_minus_generator import generate_t_minus, extract_csv
import pandas as pd

# Загрузка данных
tagged_df = pd.read_excel('batchs/S_p_m.xlsx')
found_df  = pd.read_excel('batchs/found_evidence.xlsx')
found_ids = set(found_df['id'])
model_df  = tagged_df[~tagged_df['id'].isin(found_ids)].reset_index(drop=True)
print(f"Для модели: {len(model_df)} строк")

# Тест на 10 примерах
for _, row in model_df.head(5).iterrows():
    try:
        tbl = pd.read_csv(f"data/{row['context']}", quotechar='"', on_bad_lines='skip', engine='python')
        if tbl.empty:
            print(f"❌ id={row['id']}: ПУСТАЯ ТАБЛИЦА")
            continue
        t_minus, err = generate_t_minus(row['utterance'], row['targetValue'], tbl)
        if t_minus is None:
            print(f"❌ id={row['id']}: {err}")
        else:
            print(f"\n{'='*60}")
            print(f"✅ id={row['id']}")
            print(f"S: {row['utterance']}")
            print(f"Answer: {row['targetValue']}")
            print(f"\n--- ОРИГИНАЛ ---\n{tbl.head(5).to_string(index=False)}")
            print(f"\n--- T- ---\n{t_minus}")
    except Exception as e:
        print(f"❌ id={row['id']}: {type(e).__name__} - {e}")


