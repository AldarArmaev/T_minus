import pandas as pd
import os

# Загружаем spm_with_tm_columns
spm_tm = pd.read_csv('/home/master/T_minus/T_m_log/spm_with_tm_columns.csv')
print(f"spm_with_tm_columns: {len(spm_tm)} строк")

# Папка с T_p файлами
tp_folder = '/home/master/T_minus/T_p'

# Добавляем колонку с содержимым T_p файла
tables = []

for idx, row in spm_tm.iterrows():
    file_id = row['id']
    tp_file = os.path.join(tp_folder, f"{file_id}_positive.csv")

    if os.path.exists(tp_file):
        # Читаем содержимое T_p файла как строку
        with open(tp_file, 'r', encoding='utf-8') as f:
            content = f.read()
        tables.append(content)
    else:
        # Если файла нет, оставляем пустую строку (NOT NULL, а пустая строка)
        tables.append("")
        print(f"⚠️ Не найден файл для ID: {file_id}")

# Добавляем колонку с таблицей
spm_tm['T_p_table'] = tables

found_count = len([t for t in tables if t])
print(f"✅ Найдено таблиц из T_p: {found_count} из {len(spm_tm)}")

# Сохраняем в TSV (разделитель табуляция)
output_path = '/home/master/T_minus/T_m_log/spm_with_tm_columns_and_tp.tsv'
spm_tm.to_csv(output_path, sep='\t', index=False, encoding='utf-8')
print(f"\n📁 TSV файл сохранен: {output_path}")

# Показываем пример
print("\n📋 Пример первой строки:")
print(f"id: {spm_tm.iloc[0]['id']}")
print(f"columns: {spm_tm.iloc[0]['columns']}")
print(f"T_p_table preview: {spm_tm.iloc[0]['T_p_table'][:100] if spm_tm.iloc[0]['T_p_table'] else 'EMPTY'}...")