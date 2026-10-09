import pandas as pd

# Загружаем training.tagged
tagged = pd.read_csv('data/tagged/data/training.tagged', sep='\t')
tagged['num_id'] = tagged['id'].str.replace('nt-', '').astype(int)

# Загружаем S_m_p.csv
df = pd.read_csv('/home/master/T_minus/T_m_log/S_m_p.csv')

# Добавляем колонку S_p_untagged (оригинальный вопрос без масок)
df = df.merge(tagged[['num_id', 'utterance']], left_on='id', right_on='num_id', how='left')
df.rename(columns={'utterance': 'S_p_untagged'}, inplace=True)
df.drop('num_id', axis=1, inplace=True)

# Сохраняем
df.to_csv('/home/master/T_minus/T_m_log/S_m_p_untagged.csv', index=False)
print("Готово!")