from t_minus_generator import generate_t_minus
import pandas as pd
import os
import asyncio
from tqdm import tqdm

# === НАСТРОЙКИ ===
MAX_CONCURRENT = 10
OUTPUT_FOLDER = 'T_m_retry'
FAILED_LOG = 'T_m_log/retry_failed_details.csv'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('T_m_log', exist_ok=True)


async def process_row(row, pbar, failed_details):
    """Обработка одной строки. Возвращает True если успешно, иначе False."""
    out_file = f"{OUTPUT_FOLDER}/{row['id']}_negative.csv"

    if os.path.exists(out_file):
        pbar.update(1)
        return True

    try:
        tbl = pd.read_csv(f"data/{row['context']}", quotechar='"', on_bad_lines='skip')
        tbl.columns = tbl.columns

        if tbl.empty:
            reason = "empty table"
            failed_details.append({
                'id': row['id'],
                'utterance': row['utterance'],
                'targetValue': row['targetValue'],
                'context': row['context'],
                'error': reason
            })
            pbar.write(f"❌ id={row['id']}: {reason}")
            return False

        t_minus, err = await generate_t_minus(row['utterance'], row['targetValue'], tbl)

        if t_minus is None:
            reason = err if err else "Unknown error"
            failed_details.append({
                'id': row['id'],
                'utterance': row['utterance'],
                'targetValue': row['targetValue'],
                'context': row['context'],
                'error': reason
            })
            pbar.write(f"❌ id={row['id']}: {reason}")
            return False

        # Конвертируем в строку
        if isinstance(t_minus, list):
            content = ','.join(t_minus)
        else:
            content = str(t_minus)

        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(content)

        pbar.write(f"✅ id={row['id']} -> {out_file}")
        return True

    except Exception as e:
        reason = f"{type(e).__name__} - {e}"
        failed_details.append({
            'id': row['id'],
            'utterance': row['utterance'],
            'targetValue': row['targetValue'],
            'context': row['context'],
            'error': reason
        })
        pbar.write(f"❌ id={row['id']}: {reason}")
        return False


async def run():
    # Загружаем лог ошибок
    failed_df = pd.read_csv('T_m_log/failed_details.csv', sep='\t', encoding='utf-8')

    # Фильтруем только ошибки "No valid columns found in response"
    # no_columns_df = failed_df[failed_df['error'].str.contains('No valid columns found in response', na=False)]
    no_columns_df = failed_df[failed_df['error'] == 'empty table']

    # Загружаем исходный датасет для получения полных данных
    spm = pd.read_excel('batchs/S_p_m_fixed.xlsx')

    # Создаем словарь для быстрого поиска
    spm_dict = {row['id']: row for _, row in spm.iterrows()}

    # Формируем список для повторной обработки
    to_process = []
    for _, row in no_columns_df.iterrows():
        if row['id'] in spm_dict:
            to_process.append(spm_dict[row['id']])

    print(f"Всего ошибок 'No valid columns found in response': {len(no_columns_df)}")
    print(f"Будет обработано повторно: {len(to_process)}")

    if len(to_process) == 0:
        print("Нет записей для обработки")
        return

    failed_details = []

    with tqdm(total=len(to_process), desc="Повторная генерация T-", unit="таблица") as pbar:
        for i in range(0, len(to_process), MAX_CONCURRENT):
            batch = to_process[i:i + MAX_CONCURRENT]
            tasks = [process_row(row, pbar, failed_details) for row in batch]
            await asyncio.gather(*tasks)

    # Сохраняем детали ошибок
    if failed_details:
        df_failed = pd.DataFrame(failed_details)
        df_failed.to_csv(FAILED_LOG, sep='\t', index=False, encoding='utf-8')
        print(f"\n⚠️ Снова не удалось обработать {len(failed_details)} строк. Детали сохранены в {FAILED_LOG}")

        print("\n📋 Примеры ошибок:")
        for fd in failed_details[:5]:
            print(f"  id={fd['id']}: {fd['error'][:80]}")
    else:
        print("\n✅ Все проблемные строки успешно обработаны!")

    print(f"\n📁 Результаты сохранены в папку: {OUTPUT_FOLDER}")
    total_files = len([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('_negative.csv')])
    print(f"✅ Всего создано файлов: {total_files}")


if __name__ == "__main__":
    asyncio.run(run())