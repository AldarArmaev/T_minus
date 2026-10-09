from t_minus_generator import generate_t_minus
import pandas as pd
import os
import asyncio
from tqdm import tqdm

# === НАСТРОЙКИ ===
MAX_CONCURRENT = 5
OUTPUT_FOLDER = 'T_m_test'
FAILED_LOG = 'T_m_log/failed_details_test.csv'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('T_m_log', exist_ok=True)


async def process_row(row, pbar, failed_details):
    """Обработка одной строки. Возвращает True если успешно, иначе False."""
    out_file = f"{OUTPUT_FOLDER}/{row['id']}_negative.csv"

    if os.path.exists(out_file):
        pbar.update(1)
        return True

    try:
        tbl = pd.read_csv(f"data/{row['context']}", quotechar='"', on_bad_lines='skip', engine='python')
        tbl.columns = tbl.columns.str.replace('\n', ' ').str.replace('\r', '').str.strip()

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
    # Загрузка всего датасета
    spm = pd.read_excel('batchs/S_p_m_fixed.xlsx')

    # Берем первые 50 строк для теста
    TEST_SIZE = 50
    spm = spm.head(TEST_SIZE)
    total = len(spm)
    print(f"Тестовый запуск: {total} строк (первые {TEST_SIZE})")

    to_process = []
    already_done = 0
    for _, row in spm.iterrows():
        out_file = f"{OUTPUT_FOLDER}/{row['id']}_negative.csv"
        if not os.path.exists(out_file):
            to_process.append(row)
        else:
            already_done += 1

    print(f"Уже обработано: {already_done}")
    print(f"Осталось: {len(to_process)}")

    failed_details = []

    with tqdm(total=len(to_process), desc="Генерация T-", unit="таблица") as pbar:
        for i in range(0, len(to_process), MAX_CONCURRENT):
            batch = to_process[i:i + MAX_CONCURRENT]
            tasks = [process_row(row, pbar, failed_details) for row in batch]
            await asyncio.gather(*tasks)

    # Сохраняем детали ошибок с правильным разделителем и экранированием
    if failed_details:
        df_failed = pd.DataFrame(failed_details)
        # Используем tab как разделитель, чтобы избежать проблем с запятыми
        df_failed.to_csv(FAILED_LOG, sep='\t', index=False, encoding='utf-8')
        print(f"\n⚠️ Не удалось обработать {len(failed_details)} строк. Детали сохранены в {FAILED_LOG}")

        # Показываем пример ошибок
        print("\n📋 Примеры ошибок:")
        for fd in failed_details[:3]:
            print(f"  id={fd['id']}: {fd['error'][:80]}")
    else:
        print("\n✅ Тестовые 50 строк успешно обработаны!")

    print(f"\n📁 Результаты сохранены в папку: {OUTPUT_FOLDER}")

    # Проверяем созданные файлы
    print("\n📄 Проверка созданных файлов (первые 10):")
    count = 0
    for i in range(TEST_SIZE):
        out_file = f"{OUTPUT_FOLDER}/{i}_negative.csv"
        if os.path.exists(out_file):
            with open(out_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"  id={i}: {content[:80]}")
                count += 1
        if count >= 10:
            break
    
    print(f"\n✅ Всего создано файлов: {len([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('_negative.csv')])}")


if __name__ == "__main__":
    asyncio.run(run())