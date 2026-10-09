from openai import OpenAI, AsyncOpenAI
import base64
from typing import List, Dict, Any, Callable
import inspect


def get_kwargs(kwargs: Dict[str, Any], func: Callable) -> Dict[str, Any]:
    """Вытаскивает аргументы из kwargs по сигнатуре функции func."""
    sig = inspect.signature(func)
    return {key: value for key, value in kwargs.items() if key in sig.parameters}


class ModelMessageDict(dict):
    """Класс - словарь для удобного форматирования запроса к модели."""

    def __init__(self, role: str = 'user'):
        super().__init__()
        self['role'] = role
        self['content'] = ''

    def add_text_content(self, content: str):
        self['content']+= content

    def add_img_content(self, source: str = 'image_url', path_to_img: str = None, url: str = None):
        match source:
            case 'image_url':
                if path_to_img is not None:
                    with open(path_to_img, "rb") as f:
                        base64_image = base64.b64encode(f.read()).decode()
                    self['content'].append({
                        'type': 'image_url',
                        'image_url': {'url': f"data:image/jpeg;base64,{base64_image}"}
                    })
                elif url is not None:
                    self['content'].append({
                        'type': 'image_url',
                        'image_url': {'url': url}
                    })


def send_messasge(messages, base_url: str = "http://127.0.0.1:8880/v1",
                  api_key: str = 'EMPTY', model_name: str = 'Qwen/Qwen3-VL-30B-A3B-Thinking',
                  **kwargs):
    """Синхронная версия."""
    client = OpenAI(api_key=api_key, base_url=base_url, **get_kwargs(kwargs, OpenAI))
    try:
        print(f"Generating content with model: {model_name}")
        response = client.chat.completions.create(
            messages=messages,
            model=model_name,
            **get_kwargs(kwargs, client.chat.completions.create)
        )
        return True, [answ.message.content for answ in response.choices]
    except Exception as e:
        print("Failed to call LLM: " + str(e))
        if hasattr(e, 'response'):
            try:
                error_info = e.response.json()
                code_value = error_info['error']['code']
                print(code_value)
            except:
                code_value = "parse_error"
        else:
            code_value = "context_length_exceeded"
            print(code_value)
        return False, None


async def send_messasge_async(messages, base_url: str = "http://127.0.0.1:8880/v1",
                              api_key: str = 'EMPTY',
                              model_name: str = 'Qwen/Qwen3-VL-30B-A3B-Thinking',
                              **kwargs):
    """Асинхронная версия отправки сообщений."""
    client = AsyncOpenAI(api_key=api_key, base_url=base_url, **get_kwargs(kwargs, AsyncOpenAI))
    try:
        print(f"Generating content with model: {model_name}")
        response = await client.chat.completions.create(
            messages=messages,
            model=model_name,
            **get_kwargs(kwargs, client.chat.completions.create)
        )
        return True, [answ.message.content for answ in response.choices]
    except Exception as e:
        print("Failed to call LLM: " + str(e))
        return False, None