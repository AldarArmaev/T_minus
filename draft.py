
from prompt import SYSTEM
import pandas as pd
import re
from io import StringIO
from utils import send_messasge, ModelMessageDict


def extract_csv(response: str, expected_cols: list) -> str | None:
    # Обрезаем по </think>
    if '</think>' in response:
        response = response.split('</think>')[-1].strip()

    # Убираем markdown
    response = re.sub(r'```[a-z]*\n?', '', response).replace('```', '').strip()

    # Ищем заголовки
    lines = response.split('\n')
    for i, line in enumerate(lines):
        if all(col.lower() in line.lower() for col in expected_cols[:2]):
            return '\n'.join(lines[i:])

    return response

print(extract_csv('''        Let me check: 
          The string: "Resigned to accept position as Minister Plenipotentiary to Russia" -> no comma? 

        So it's safe? 

        Therefore, we output as above.

        We are done.
</think>

Unnamed: 0,Name,Took office,Left office,Party,Notes/Events
11,William Pinkney,"March 4, 1803","March 3, 1805",Democratic Republican,
12,Alexander McKim,"March 4, 1809","March 3, 1815",Democratic Republican,
13,William Pinkney,"March 4, 1815","April 18, 1816",Democratic Republican,Resigned to accept position as Minister Plenipotentiary to Russia
14,Peter Little,"September 2, 1816","March 3, 1823",Democratic Republican,
14,Peter Little,"March 4, 1823","March 3, 1825",Jacksonian DR,
14,Peter Little,"March 4, 1825","March 3, 1829",Adams,
15,Benjamin C. Howard,"March 4, 1829","March 3, 1833",Jacksonian,
''',['Name','Took office','Left office','Party,Notes/Events']))