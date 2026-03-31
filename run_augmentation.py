from t_minus_generator import generate_t_minus
import pandas as pd
import os
from tqdm import tqdm

# Загрузка данных
tagged_df = pd.read_excel('batchs/S_p_m.xlsx')
found_df  = pd.read_excel('batchs/found_evidence.xlsx')
found_ids = set(found_df['id'])
model_df  = tagged_df[~tagged_df['id'].isin(found_ids)].reset_index(drop=True)
print(f"Для модели: {len(model_df)} строк")

os.makedirs('data/tables', exist_ok=True)
CHECKPOINT_FILE = 'batchs/t_minus_results.xlsx'
FAILED_FILE     = 'batchs/t_minus_failed.xlsx'
SAVE_EVERY      = 50

results, failed = [], []
done_ids = set()
if os.path.exists(CHECKPOINT_FILE):
    done_df  = pd.read_excel(CHECKPOINT_FILE)
    results  = done_df.to_dict('records')
    done_ids = set(done_df['id'])
    print(f"Чекпоинт: уже готово {len(done_ids)} строк")

# run_augmentation.py (только изменённая часть)

for _, row in tqdm(model_df.iterrows(), total=len(model_df), desc="Генерация T-", unit="таблица"):
    if row['id'] in done_ids:
        continue

    try:
        tbl = pd.read_csv(f"data/{row['context']}", quotechar='"', on_bad_lines='skip', engine='python')

        if tbl.empty:
            failed.append({**row.to_dict(), 'error': 'empty table'})
            tqdm.write(f"❌ id={row['id']}: пустая таблица")
            continue

        t_minus, err = generate_t_minus(row['utterance'], row['targetValue'], tbl)

        if t_minus is None:
            failed.append({**row.to_dict(), 'error': err})
            tqdm.write(f"❌ id={row['id']}: {err}")
        else:
            path = f"data/tables/{row['id']}_negative.csv"
            t_minus.to_csv(path, index=False, encoding='utf-8')
            results.append({**row.to_dict(), 'T_minus_path': path})
            tqdm.write(f"✅ id={row['id']} -> {path}")

    except Exception as e:
        failed.append({**row.to_dict(), 'error': str(e)})
        tqdm.write(f"❌ id={row['id']}: {type(e).__name__} - {e}")

    # Чекпоинт каждые 50 строк
    if (len(results) + len(failed)) % SAVE_EVERY == 0:
        pd.DataFrame(results).to_excel(CHECKPOINT_FILE, index=False)
        pd.DataFrame(failed).to_excel(FAILED_FILE, index=False)
        tqdm.write(f"💾 Чекпоинт сохранён ({len(results)} успешно, {len(failed)} ошибок)")

pd.DataFrame(results).to_excel(CHECKPOINT_FILE, index=False)
pd.DataFrame(failed).to_excel(FAILED_FILE, index=False)
print(f"✅ Успешно: {len(results)}")
print(f"⚠️ Failed: {len(failed)}")