import pandas as pd
import os

# Загружаем исходные данные
spm = pd.read_excel('/home/master/T_minus/batchs/S_p_m_fixed.xlsx')
total_ids = set(spm['id'])
print(f"Всего записей в S_p_m_fixed: {len(total_ids)}")

# Загружаем обработанные из T_m
tm_ids = set()
if os.path.exists('/home/master/T_minus/T_m_log/T_m_all_columns.csv'):
    tm_df = pd.read_csv('/home/master/T_minus/T_m_log/T_m_all_columns.csv')
    tm_ids.update(tm_df['id'].tolist())
    print(f"Обработано в T_m: {len(tm_df)}")
    print(f"Уникальных ID в T_m: {len(tm_ids)}")

# Загружаем обработанные из T_m_retry
if os.path.exists('/home/master/T_minus/T_m_log/T_m_retry_all_columns.csv'):
    tm_retry_df = pd.read_csv('/home/master/T_minus/T_m_log/T_m_retry_all_columns.csv')
    tm_ids.update(tm_retry_df['id'].tolist())
    print(f"Обработано в T_m_retry: {len(tm_retry_df)}")
    print(f"Всего уникальных ID после объединения: {len(tm_ids)}")

# Загружаем логи ошибок
failed_df = pd.read_csv('/home/master/T_minus/T_m_log/failed_details.csv', sep='\t', encoding='utf-8')
print(f"Всего ошибок в логе: {len(failed_df)}")

# Создаем словарь ошибок по ID
error_map = {}
for _, row in failed_df.iterrows():
    error_map[row['id']] = row['error']

# Находим необработанные
unprocessed_ids = total_ids - tm_ids
print(f"Не обработано: {len(unprocessed_ids)}")

# Сохраняем необработанные с информацией об ошибках
if unprocessed_ids:
    unprocessed_df = spm[spm['id'].isin(unprocessed_ids)].copy()

    # Добавляем колонку с типом ошибки
    unprocessed_df['error_type'] = unprocessed_df['id'].map(error_map)
    unprocessed_df['error_type'] = unprocessed_df['error_type'].fillna('not_in_failed_log')

    output_file = '/home/master/T_minus/T_m_log/unprocessed_tables.xlsx'
    unprocessed_df.to_excel(output_file, index=False)
    print(f"\n📁 Необработанные таблицы сохранены в: {output_file}")

    print(f"\n📊 Статистика по типам ошибок среди необработанных:")
    print(unprocessed_df['error_type'].value_counts())

    print(f"\n📋 Примеры необработанных ID (первые 20):")
    print(sorted(list(unprocessed_ids))[:20])
else:
    print("\n✅ Все таблицы обработаны!")