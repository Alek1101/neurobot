import logging

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, languages
from gpt import count_tokens, ask_gpt

bot = telebot.TeleBot(TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d.%m.%Y, %H:%M:%S',
    filename='logs_file.txt',
    filemode='w'
)

user_data = []


def language_(text: str):
    if text in languages:
        return True
    else:
        return False


def create_keyboard(options):
    buttons = (KeyboardButton(text=option) for option in options)
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(commands=['debug'])
def debug(m):
    try:
        with open('logs_file.txt', 'r') as f:
            bot.send_document(m.chat.id, f)
    except:
        bot.send_message(m.chat.id, 'Не удалось прислать файл с логами')
        logging.warning('Не удалось отправить документ с логами')


@bot.message_handler(commands=['start'])
def start(m):
    name = m.from_user.first_name
    bot.send_message(m.chat.id, f'Привет, {name}!\nТы можешь задать мне вопрос о языках программирования.')
    bot.send_message(m.chat.id, 'Список доступных команд:\n'
                                '/list  - поддерживаемые ботом языки программирования\n'
                                '/ask - задать вопрос', reply_markup=create_keyboard(['/list', '/ask']))


@bot.message_handler(commands=['list'])
def names(m):
    bot.send_message(m.chat.id, text='\n'.join(languages))


@bot.message_handler(commands=['ask'])
def ask_bot(m):
    bot.send_message(m.chat.id, 'Задайте свой вопрос об одном из следующих языков программирования:',
                     reply_markup=create_keyboard(languages))
    bot.register_next_step_handler(m, language_choice)


def language_choice(m):
    if not language_(m.text):
        bot.send_message(m.chat.id, 'Выберите один из представленных языков программирования:',
                         reply_markup=create_keyboard(languages))
        bot.register_next_step_handler(m, language_choice)
    else:
        language = m.text
        user_data.append(language)
        bot.send_message(m.chat.id, 'Выберите свой уровень: ',
                         reply_markup=create_keyboard(['начинающий', 'продвинутый']))
        bot.register_next_step_handler(m, level_choice)


def level_choice(m):
    if m.text not in ['начинающий', 'продвинутый']:
        bot.send_message(m.chat.id, 'Выберите свой уровень: ',
                         reply_markup=create_keyboard(['начинающий', 'продвинутый']))
        bot.register_next_step_handler(m, level_choice)
    else:
        level = m.text
        user_data.append(level)
        bot.send_message(m.chat.id, 'Задайте свой вопрос')
        bot.register_next_step_handler(m, gpt_answer)


def gpt_answer(m):
    task = m.text
    if not count_tokens(task):
        bot.send_message(m.chat.id, 'Слишком длинный вопрос.\nПопробуйте ещё раз.')
        bot.register_next_step_handler(m, gpt_answer)
    else:
        user_data.append(task)
        bot.send_message(m.chat.id, 'Вопрос принят, ожидайте ответа...')
        try:
            bot.send_message(m.chat.id, ask_gpt(user_data[0], user_data[1], user_data[2]),
                             reply_markup=create_keyboard(['завершить ответ', 'продолжить ответ']))
        except:
            bot.send_message(m.chat.id, 'Не удалось получить ответа от нейросети.\nПопробуйте ещё раз.')
            logging.warning('Ошибка при генерации ответа нейросетью.')
            bot.register_next_step_handler(m, gpt_answer)


def gpt_continue(m):
    if m.text == 'завершить ответ':
        bot.send_message(m.chat.id, 'Ответ завершён')
    # elif m.text == 'продолжить ответ':



bot.polling()
