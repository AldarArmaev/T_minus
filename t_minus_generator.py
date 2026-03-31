from prompt import SYSTEM
import pandas as pd
import re
from io import StringIO
from utils import send_messasge, ModelMessageDict


def extract_csv(response: str, expected_cols: list) -> str | None:
    # Обрезаем по </think>
    if '</think>' in response:
        response = response.split('</think>')[-1].strip()

    # # Убираем markdown
    # response = re.sub(r'```[a-z]*\n?', '', response).replace('```', '').strip()
    #
    # # Ищем заголовки
    # lines = response.split('\n')
    # for i, line in enumerate(lines):
    #     if all(col.lower() in line.lower() for col in expected_cols[:2]):
    #         return '\n'.join(lines[i:])

    return response

def generate_t_minus(question, answer, tbl, max_rows=20):
    tbl_input = tbl.head(max_rows) if len(tbl) > max_rows else tbl
    msg = ModelMessageDict(role='user')
    msg.add_text_content(
        f"QUESTION: {question}\nANSWER: {answer}\nTABLE:\n{tbl_input.to_string(index=False)}\nOUTPUT:"
    )
    success, responses = send_messasge(
        messages=[{"role": "system", "content": SYSTEM}, msg],
        base_url="http://192.168.19.148:8888/v1",
        #base_url="http://localhost:8880/v1",
        api_key='EMPTY',
        model_name='Qwen/Qwen3-VL-32B-Thinking',
        temperature=0.3,
    )
    #print(responses[0])
    if not success:
        return None, f"LLM error: {responses}"
    response = responses[0]
    csv_text = extract_csv(response, list(tbl_input.columns))
    # t_minus = pd.read_csv(StringIO(csv_text))
    # if list(t_minus.columns) != list(tbl_input.columns):
    #     return None, "columns mismatch"
    # if len(t_minus) != len(tbl_input):
    #     return None, "rows mismatch"
    # if tbl_input.equals(t_minus):
    #     return None, "identical to original"
    return csv_text, None
    # return t_minus, None