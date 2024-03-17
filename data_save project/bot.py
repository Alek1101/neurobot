import logging

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, languages
from gpt import count_tokens, ask_gpt, str_sew
import database

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
    user_id = m.from_user.id
    database.create_table()
    database.delete_data(user_id)
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
        # user_data.append(language)
        id = m.from_user.id
        database.insert_row([id, language, '', '', ''])
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
        user_id = m.from_user.id
        database.update_data(user_id, 'level', level)
        bot.send_message(m.chat.id, 'Задайте свой вопрос')
        bot.register_next_step_handler(m, gpt_answer)


def gpt_answer(m):
    task = m.text
    user_id = m.from_user.id
    if not count_tokens(task):
        bot.send_message(m.chat.id, 'Слишком длинный вопрос.\nПопробуйте ещё раз.')
        bot.register_next_step_handler(m, gpt_answer)
    else:
        database.update_data(user_id, 'task', task)
        bot.send_message(m.chat.id, 'Вопрос принят, ожидайте ответа...')
        try:
            answer = ask_gpt(database.get_data_for_user(user_id)[2],
                             database.get_data_for_user(user_id)[3],
                             database.get_data_for_user(user_id)[4])
            print(answer)
            bot.send_message(m.chat.id, answer, reply_markup=create_keyboard(['завершить ответ', 'продолжить ответ']))
            database.update_data(user_id, 'answer', str_sew(answer))
            bot.register_next_step_handler(m, gpt_continue)
        except:
            bot.send_message(m.chat.id, 'Не удалось получить ответа от нейросети.\nПопробуйте ещё раз.')
            logging.warning('Ошибка при генерации ответа нейросетью.')
            bot.register_next_step_handler(m, gpt_answer)


def gpt_continue(m):
    user_id = m.from_user.id
    if m.text == 'завершить ответ':
        bot.send_message(m.chat.id, 'Ответ завершён')
        database.delete_data(user_id)
    elif m.text == 'продолжить ответ':
        bot.send_message(m.chat.id, 'Продолжаю ответ...')
        try:
            answer = ask_gpt(database.get_data_for_user(user_id)[2],
                             database.get_data_for_user(user_id)[3],
                             database.get_data_for_user(user_id)[4],
                             database.get_data_for_user(user_id)[5])
            database.update_data(user_id, 'answer', str_sew(answer))
            bot.send_message(m.chat.id, answer, reply_markup=create_keyboard(['завершить ответ', 'продолжить ответ']))
            bot.register_next_step_handler(m, gpt_continue)
        except:
            bot.send_message(m.chat.id, 'Не удалось получить ответа от нейросети.\nПопробуйте ещё раз.')
            logging.warning('Ошибка при генерации ответа нейросетью.')
            bot.register_next_step_handler(m, gpt_continue)


bot.polling()
