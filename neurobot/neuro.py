import requests
from transformers import AutoTokenizer
from config import TOKENS_LENGTH, temperature, HEADERS, GPT_LOCAL_URL

system_content = ('Ты - дружелюбный помощник для ответов на вопросы по программированию. '
                  'Определи, на каком языке программирования написан код, и дай подробный ответ на поставленный вопрос'
                  ' на '
                  'русском языке.')
assistant_content = 'Реши задачу по шагам: '

messages = [
    {'role': 'system', 'content': system_content}
]

task = ''


def ask(user_message: str):
    prompt = user_message
    global task
    if prompt == '/continue':
        task = assistant_content + task
    else:
        task = prompt
    messages.append({'role': 'user', 'content': task})
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
        return result, True
    else:
        return response.json(), False


def count_tokens(prompt: str):
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")  # название модели
    return len(tokenizer.encode(prompt))


import json


def save_progress(user_id, question_number):
    cur_progress = {str(user_id): question_number}
    try:
        with open('users_data.json', 'r') as file:
            progress = json.load(file)
        progress[str(user_id)] = question_number
        with open('users_data.json', 'w') as file:
            json.dump(cur_progress, file)
    except:
        with open('users_data.json', 'w') as file:
            json.dump(cur_progress, file)


def load_progress(user_id):
    try:
        with open('users_data.json', 'r') as file:
            progress = json.load(file)
            return progress.get(str(user_id))
    except:
        return 'error'
