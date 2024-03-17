import requests
from transformers import AutoTokenizer
from config import TOKENS_LENGTH, HEADERS, GPT_LOCAL_URL, temperature


def ask_gpt(language: str, level: str, question: str, assistant_content=None):
    system_content = (f'Ты - дружелюбный помощник для ответов на вопросы по языку программирования {language}.'
                      f'Дай ответ на заданный вопрос. Уровень понимания пользователем языка - {level}.'
                      f'Учитывай уровень пользователя при ответе.')
    messages = [{'role': 'system', 'content': system_content}, {'role': 'user', 'content': question},
                {'role': 'assistant', 'content': assistant_content}]
    response = requests.post(
        url=GPT_LOCAL_URL,
        headers=HEADERS,
        json={
            'messages': messages,
            'temperature': temperature,
            'max_tokens': TOKENS_LENGTH
        }
    )
    if response.status_code == 200:
        result = response.json()['choices'][0]['message']['content']
        return result
    else:
        return response.json()


def count_tokens(prompt: str):
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")  # название модели
    if len(tokenizer.encode(prompt)) > TOKENS_LENGTH:
        return False
    else:
        return True


def str_sew(text: str):
    a = text.split()
    a = ''.join(a)
    return a


