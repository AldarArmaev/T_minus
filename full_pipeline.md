S+
Пример создания S+ https://chat.deepseek.com/share/y0jw674w5bxraqg4xi
Пример проверки результата S+ https://chat.deepseek.com/share/z3xgohzvqh1r07pupb
Проверяли наличие слов с именнованными сущностями из оригинала в перефразе (использовали точное совпадение) https://chat.deepseek.com/share/pm8jphrxv3vlnefvrf 

==========================================================================================================================================================
S- 
Заменяется слово на противоположное:  'shortest': 'longest' и так далее
Если не удалось заменить то нейронка изменяет: https://chat.deepseek.com/share/e9f0vybu6c2xwx1bp6


Что это значит: в ~11.5% перефразов LLM "потеряла" хотя бы одну именованную сущность из оригинала. Это сигнал, что перефразы местами неэквивалентны оригиналу по смыслу (например, "Los Angeles" → "the city").

⚠️ Важные ограничения метода
Наш подход использует точное совпадение слов — это просто, но есть нюансы:

Ложные потери:

Оригинал: "piotr's" → перефраз: "Piotr" — слово piotr найдется, а 's вообще O, всё ок.

Оригинал: "New York" → перефраз: "NYC" — код решит, что NER потеряны, хотя смысл сохранен.

Ложные сохранения: если слово встречается в перефразе в другом контексте — код засчитает как сохранение.

Не проверяем теги: код не проверяет, что LOCATION остался LOCATION. Слово может быть на месте, но с другим смыслом.

Не проверяем лишние NER в перефразе (которых не было в оригинале).







import pandas as pd
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

EXT_TRIG = {
    'shortest': 'longest', 'longest': 'shortest',
    'tallest': 'shortest',
    'lightest': 'heaviest', 'heaviest': 'lightest',
    'smallest': 'largest', 'largest': 'smallest',
    'biggest': 'smallest',
    'earliest': 'latest', 'latest': 'earliest',
    'oldest': 'youngest', 'youngest': 'oldest',
    'worst': 'best', 'best': 'worst',
    'lowest': 'highest', 'highest': 'lowest',
    'most': 'least', 'least': 'most',
    'higher': 'lower', 'lower': 'higher',
    'more': 'less', 'less': 'more',
    'larger': 'smaller', 'smaller': 'larger',
    'older': 'younger', 'younger': 'older',
    'bigger': 'smaller',
    'equal': 'different', 'different': 'equal',
    'same': 'different',
    'first': 'last', 'last': 'first',
    'second': 'second to last',
    'third': 'third to last',
    'only': 'not only',
    'never': 'always', 'always': 'never',
    'all': 'none', 'none': 'all',
    'each': 'none', 'every': 'none',
    'was': 'was not', 'was not': 'was',
    'is': 'is not', 'is not': 'is',
    'are': 'are not', 'are not': 'are',
    'were': 'were not', 'were not': 'were',
    'sum': 'average', 'average': 'sum',
    'total': 'average',
    'previous': 'next', 'next': 'previous',
    'before': 'after', 'after': 'before'
}

def load_tagged(path: str):
    df = pd.read_csv(path, sep='\t')
    ner_idx = {
        str(r.utterance).lower().strip(): list(zip(str(r.tokens).split('|'), str(r.nerTags).split('|')))
        for r in df.itertuples()
    }
    return df, ner_idx

def make_S_minus(utterance: str) -> str:
    s = utterance.lower()
    for k, v in EXT_TRIG.items():
        if k in s:
            return s.replace(k, v, 1)
    return s

def find_evidence(tbl: pd.DataFrame, utterance: str, target: str = '') -> tuple[list, list]:
    # 1. Формируем словарь токенов (вопрос + ответы)
    tokens = set(utterance.lower().split())
    for t in target.split('|'):
        tokens.update(norm(t).split())

    linked_rows, linked_cols = set(), set()

    # --- ДОБАВЛЕНО: Проверка заголовков столбцов ---
    for col in tbl.columns:
        if set(str(col).lower().split()) & tokens:
            linked_cols.add(col)
    # ----------------------------------------------

    # 2. Поиск в ячейках (без изменений)
    for r_idx, row in tbl.iterrows():
        for c_idx, val in enumerate(row):
            cell_words = set(str(val).lower().split())
            if cell_words & tokens:
                linked_rows.add(r_idx)
                linked_cols.add(tbl.columns[c_idx])

    # 3. Очистка (Pruning)
    important_rows = [r for r in linked_rows
                      if any(set(str(tbl.at[r, c]).lower().split()) & tokens
                             for c in linked_cols)]

    return important_rows, list(linked_cols)


def make_T_plus(tbl: pd.DataFrame, utterance: str) -> pd.DataFrame:
    """Оставляет только улики (important_rows × important_cols), перемешивает."""
    important_rows, important_cols = find_evidence(tbl, utterance)
    
    cols = important_cols if important_cols else list(tbl.columns)
    rows = important_rows if important_rows else list(tbl.index)
    
    t_plus = tbl.loc[rows, cols].sample(frac=1, axis=0).sample(frac=1, axis=1)
    return t_plus.reset_index(drop=True)


# ─── T-: Саботаж улики ────────────────────────────────────────────────────────
def make_T_minus(tbl: pd.DataFrame, utterance: str, all_contexts: list) -> pd.DataFrame:
    import random
    important_rows, important_cols = find_evidence(tbl, utterance)
    
    if not important_rows and not important_cols:
        fallback_ctx = random.choice(all_contexts)
        try:
            return pd.read_csv(os.path.join('data', fallback_ctx), quotechar='"', on_bad_lines='skip')
        except:
            return tbl
    
    t_minus = tbl.reset_index(drop=True).copy().astype(object)  # ← фикс здесь
    
    mask_row = bool(important_rows) and (not important_cols or random.random() > 0.5)
    if mask_row:
        r = random.choice(important_rows)
        t_minus.loc[r, :] = '[MASK]'
    else:
        c = random.choice(important_cols)
        t_minus[c] = '[MASK]'
    
    return t_minus


def test_drive(n=1):
    tagged_path = 'data/tagged/data/training.tagged'
    df, ner_index = load_tagged(tagged_path)
    all_contexts = df['context'].tolist()  # для fallback T-
    df = df.head(n)

    pd.set_option('display.max_columns', 5)
    pd.set_option('display.width', 120)
    pd.set_option('display.max_colwidth', 15)

    for i, row in df.iterrows():
        q, target, ctx = row['utterance'], str(row['targetValue']), row['context']
        try:
            s_minus = make_S_minus(q)
            tbl     = pd.read_csv(os.path.join('data', ctx))
            t_plus  = make_T_plus(tbl, q)
            t_minus = make_T_minus(tbl, q, all_contexts)

            print(f"\n{'='*30} Пример №{i+1} {'='*30}")
            print(f"S:  {q}\nS-: {s_minus}\nTarget: {target}")
            print(f"\n--- T (оригинал) ---\n{tbl.head(10).to_string(index=False)}")
            print(f"\n--- T+ ---\n{t_plus.to_string(index=False)}")
            print(f"\n--- T- ---\n{t_minus.head(10).to_string(index=False)}")

        except Exception as e:
            print(f"\n--- Пример №{i+1} --- ОШИБКА: {e}")

if __name__ == "__main__":
    test_drive(1)


==========================================================================================================================================================

T-
нейронке скармливается вопрос и таблица, и она должна вернуть список столбцов без которых невозможно ответить на вопрос, потом эти столбцы удаляются
Промпт по которой работала нейронка

SYSTEM = """Given a QUESTION, ANSWER, and TABLE — return a list of key column names without which the correct answer CANNOT be derived.

## STRICT RULES:
1. Output ONLY a comma-separated list of column names. No markdown, no explanations, no extra text.
2. Column names must exactly match the original table headers (case-sensitive, spaces preserved).
3. The answer must be impossible to derive if ANY of the listed columns are removed.
4. The list should be minimal — removing any single column should make the answer impossible to derive.
5. Assume all other columns (not listed) are still present.

## CRITICAL: HANDLE CALCULATIONS AND AGGREGATIONS
- If the question asks for AVERAGE, SUM, MAX, MIN, COUNT → return the numeric column + grouping column if needed
- Example: "average number of years" → return the 'Years' column (the model can calculate average from it)
- Example: "total points" → return the 'Points' column
- Example: "how many games did X win" → return columns for filtering (e.g., 'Winner') + counting (e.g., 'Game')

## CRITICAL: HANDLE COMPARISONS AND SEQUENCES
- "higher than", "less than", "more than" → return columns for comparison values
- "next after X", "previous to X" → return ordering column (e.g., 'Date', 'Rank') + value column
- "largest", "smallest", "least", "most" → return column to compare + column to measure

## CRITICAL: HANDLE MISSING OR SIMILAR COLUMNS
- If exact column name doesn't exist, use the semantically closest column from the available headers
- For "years served" and column 'Years' exists → use 'Years'
- For "took office" and column 'Took office' exists → use 'Took office'
- For "agricultural volume" and year columns exist → use the year column that contains the answer

## STRATEGIES BY QUESTION TYPE:

**Filtering questions** (WHERE condition):
   "what was the X when Y = Z" → return column for filtering (Y) + column for answer (X)

**Aggregation questions** (AVG, SUM, COUNT):
   "average number of X" → return the numeric column X (no grouping needed, model can compute)
   "total number of X" → return column X

**Extreme value questions** (MAX, MIN, LARGEST, SMALLEST):
   "largest X" → return column X (model can find max)
   "which team had the most wins" → return 'Team' + 'Wins' (or just 'Wins' if team is row identifier)

**Comparison questions** (HIGHER/LOWER THAN):
   "did X have more than Y" → return column with values to compare

**Sequence questions** (NEXT, PREVIOUS, FIRST, LAST):
   "what was the next X after Y" → return ordering column + identifying column
   "what was the first year" → return year column

**Lookup questions** (DIRECT MATCH):
   "who was the first ambassador" → return column with names + ordering column if needed

## EXAMPLES:

EXAMPLE_1
QUESTION: what was the last year where this team was a part of the usl a-league?
ANSWER: 2004
TABLE: Year,Division,League,Regular Season,Playoffs,Open Cup,Avg. Attendance
2001,2,USL A-League,"4th, Western",Quarterfinals,Did not qualify,7169
2002,2,USL A-League,"2nd, Pacific",1st Round,Did not qualify,6260
2003,2,USL A-League,"3rd, Pacific",Did not qualify,Did not qualify,5871
2004,2,USL A-League,"1st, Western",Quarterfinals,4th Round,5628
2005,2,USL First Division,5th,Quarterfinals,4th Round,6028
OUTPUT: Year,League

EXAMPLE_2
QUESTION: what was the average number of years served by a coach?
ANSWER: 4
TABLE: Coach, Tenure, Record, Years, Pct.
Joe Sewell, 1931-1936, 221-122-16, 6, .637
OUTPUT: Years

EXAMPLE_3
QUESTION: who was the first to take office?
ANSWER: Jaafar Mohamed
TABLE: Menteri Besar, #, Party, Took office, Left office
Jaafar Mohamed, 1, BN, 21 May 2018, -
OUTPUT: Took office

EXAMPLE_4
QUESTION: which year had the largest agricultural volume?
ANSWER: 2010/11
TABLE: 2007/08, 2008/09, 2009/10, 2010/11, 2011/12, IME Exchange (Including spot, credit and forward transactions)
100, 150, 200, 300, 250, 12345
OUTPUT: 2010/11

EXAMPLE_5
QUESTION: what is the next highest hard drive available after the 30gb model?
ANSWER: 64GB SSD
TABLE: Model 01+, Component, Model e2, Model 01, model 03 (China Copy), Model 2+ (Pre-production), Model 02
OUTPUT: Component,Model 02

EXAMPLE_6
QUESTION: what is the average score of all home team members for all dates?
ANSWER: 1.75
TABLE: Home team, Away team, Date, Score, Notes
Team A, Team B, 2024-01-01, 2, -
Team C, Team D, 2024-01-02, 1.5, -
OUTPUT: Score

EXAMPLE_7
QUESTION: how many games did new zealand win in 2010?
ANSWER: 3
TABLE: Date, Venue, Score, Victor, Comments, Match reports
27 November 2010, Millennium Stadium, 25-37, New Zealand, 2010 Autumn International, BBC
26 June 2010, Waikato Stadium, 29-10, New Zealand, 2010 mid-year rugby test series, -
19 June 2010, Carisbrook, 42-9, New Zealand, 2010 mid-year rugby test series, Stuff
OUTPUT: Victor,Date

EXAMPLE_8
QUESTION: what number of games did new zealand win?
ANSWER: 3
TABLE: Date, Venue, Score, Victor, Comments, Match reports
OUTPUT: Victor

## REMEMBER:
- Return ONLY column names, NOT data
- If the answer requires a calculation, return the numeric column(s)
- If the question asks for a specific value that IS a column name (like a year), return that column
- Be minimal but sufficient - prefer single column when possible
- Do NOT add explanations, markdown, or any extra text outside the comma-separated list"""


==========================================================================================================================================================

T+ 
Перемешивание строк и столбцов
