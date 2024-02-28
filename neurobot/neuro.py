import requests

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
        'http://158.160.135.104:1234/v1/chat/completions',
        headers={'Content-Type': 'application/json'},
        json={
            'messages': messages,
            'temperature': 1.2,
            'max_tokens': 2048
        }
    )
    try:
        result = response.json()['choices'][0]['message']['content']
        return result, True
    except:
        return 'Произошла ошибка при генерации ответа', False


import json


def save_progress(user_id, question_number):
    cur_progress = {str(user_id): question_number}
    try:
        with open('users_data.json', 'r') as file:
            progress = json.load(file)
        progress[str(user_id)] = question_number.encode('utf8')
        with open('users_data.json', 'w') as file:
            json.dump(cur_progress, file)
    except:
        with open('users_data.json', 'w') as file:
            json.dump(cur_progress, file)


# Загрузка прогресса пользователя из json


def load_progress(user_id):
    try:
        with open('users_data.json', 'r') as file:
            progress = json.load(file)
            return progress.get(str(user_id)).decode('utf8')
    except FileNotFoundError:
        return None
