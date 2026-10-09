from prompt import SYSTEM
import pandas as pd
from utils import send_messasge_async, ModelMessageDict
import asyncio


def extract_columns_list(response: str):
    """
    Извлекает список имен колонок из ответа модели.
    Ожидает формат: "Col1, Col2, Col3" или просто "Col1,Col2"
    """
    # Убираем markdown блоки если есть
    if '```' in response:
        response = response.split('```')[-1].strip()

    # Разбиваем по запятой, убираем пробелы и кавычки
    cols = [c.strip().strip('"').strip("'") for c in response.split(',')]
    return cols


async def generate_t_minus(question, answer, tbl, max_rows=20):
    tbl_input = tbl.head(max_rows) if len(tbl) > max_rows else tbl

    # Получаем список колонок таблицы
    available_columns = list(tbl_input.columns)

    # Формируем сообщение пользователя с явным указанием доступных колонок
    user_msg = ModelMessageDict(role='user')
    user_msg.add_text_content(
        f"QUESTION: {question}\n"
        f"ANSWER: {answer}\n"
        f"AVAILABLE COLUMNS: {', '.join(available_columns)}\n"
        f"TABLE:\n{tbl_input.to_string(index=False)}"
    )

    success, responses = await send_messasge_async(
        messages=[{"role": "system", "content": SYSTEM}, user_msg],
        base_url="http://192.168.19.127:9886/v1",
        api_key='EMPTY',
        model_name='Qwen/Qwen3-4B-Instruct-2507',
        temperature=0.3,
    )

    if not success:
        return None, f"LLM error: {responses}"

    response = responses[0]

    # 1. Извлекаем список колонок из ответа
    selected_cols = extract_columns_list(response)

    # 2. Фильтруем: оставляем только те, что есть в оригинале
    original_cols = set(tbl_input.columns)
    valid_cols = [c for c in selected_cols if c in original_cols]

    if not valid_cols:
        return None, f"No valid columns found in response: {selected_cols}. Available: {list(original_cols)}"

    # 3. Возвращаем список колонок
    return valid_cols, None