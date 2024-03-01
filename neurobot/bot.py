import telebot
from config import TOKEN, TOKENS_LENGTH
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from neuro import ask, save_progress, load_progress, count_tokens
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d.%m.%Y, %H:%M:%S',
    filename='log_file.txt',
    filemode='w'
                    )

bot = telebot.TeleBot(TOKEN)

check = False


@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker'])
def text_filter(m):
    user = m.from_user.first_name
    if type(m.from_user.last_name) is str:
        user += m.from_user.last_name
    user_id = m.from_user.id
    bot.send_message(m.chat.id, 'Бот воспринимает только сообщения...')
    logging.debug(f'Попытка взломать систему, пользователь {user}, id = {user_id}.')


@bot.message_handler(commands=['start'])
def start(m):
    logging.debug('Команда /start активирована')
    user = m.from_user.first_name
    if type(m.from_user.last_name) is str:
        user += m.from_user.last_name
    user_id = m.from_user.id
    logging.info(f'Активация бота пользователем {user}, id = {user_id}')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('/solve_task'))
    bot.send_message(m.chat.id, 'Привет! Я - Telegram-бот с подключённой нейросетью, созданный, чтобы отвечать'
                                ' на твои вопросы. Задавай мне вопросы на тему программирования, и я постараюсь '
                                'качественно '
                                'на них ответить.')
    bot.send_message(m.chat.id, 'Для того, чтобы задать вопрос, используй команду /solve_task.', reply_markup=markup)


@bot.message_handler(commands=['solve_task'])
def instruction(m):
    logging.debug('Команда /solve_task активирована')
    bot.send_message(m.chat.id, 'Я отвечаю на вопросы на тему программирования, \nнапиши свой вопрос кратко '
                                'и точно и укажи язык программирования, о котором идёт речь, '
                                '\nа также язык, на котором '
                                ' мне следует тебе ответить.')
    bot.send_message(m.chat.id, 'Следующим сообщением отправь свой вопрос.')
    bot.register_next_step_handler(m, question_treatment)


def question_treatment(m):
    user_id = m.from_user.id
    global check
    check = False
    user = m.from_user.first_name
    if type(m.from_user.last_name) is str:
        user += m.from_user.last_name
    if m.content_type != 'text':
        logging.debug(f'Попытка отправить особое медиа, пользователь {user}, id = {user_id}')
        bot.send_message(m.chat.id, 'Отправь промт текстовым сообщением')
        bot.register_next_step_handler(m, question_treatment)
        return
    if m.text[0] == '/':
        logging.debug(f'Попытка обойти систему, пользователь {user} с id = {user_id}')
        bot.send_message(m.chat.id, 'Сначала задай свой вопрос.')
        bot.register_next_step_handler(m, question_treatment)
        return
    user_prompt = m.text
    if count_tokens(user_prompt) >= TOKENS_LENGTH:
        logging.debug('Превышено допустимое количество символов.')
        logging.info(f'Пользователь {user}, id = {user_id} превысил допустимое количество символов.')
        bot.send_message(m.chat.id, 'Количество символов превышает допустимый порог.\n'
                                    'Пожалуйста, повтори вопрос.')
        bot.register_next_step_handler(m, question_treatment)
        return
    logging.info(f'Пользователь {user}, id = {user_id} задал вопрос:\n< {user_prompt} >')
    save_progress(user_id, user_prompt)
    bot.send_message(m.chat.id, 'Промт принят! \nВремя ожидания до 5 минут.')
    check = True
    try:
        bot.send_message(m.chat.id, ask(user_prompt))
        logging.debug('Генерация ответа завершена')
    except:
        bot.send_message(m.chat.id, 'Возникла проблема при генерации ответа...\nМы уже работаем над этим.')
        logging.warning('Ошибка при генерации ответа нейросетью')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('/continue', '/solve_task')
    bot.send_message(m.chat.id, '/continue для продолжения, \n'
                                '/solve_task - для нового вопроса.', reply_markup=markup)


@bot.message_handler(commands=['continue'])
def question_continuation(m):
    logging.debug('Команда /continue активирована')
    user_id = m.from_user.id
    user = m.from_user.first_name
    if type(m.from_user.last_name) is str:
        user += m.from_user.last_name
    if check:
        bot.send_message(m.chat.id, 'Продолжение ответа...')
        # try:
        if not load_progress(id) == 'error':
            answer = ask('Продолжи:' + load_progress(id))
        else:
            answer = 'Не удалось получить ответ от нейросети'
            logging.warning('Ошибка открытия файла')
        bot.send_message(m.chat.id, answer)
        logging.debug('Генерация ответа завершена')
        # except:
        #     bot.send_message(m.chat.id, 'Возникла проблема при генерации ответа...\nМы уже работаем над этим.')
        #     logging.warning('Ошибка при генерации ответа нейросетью')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('/continue', '/solve_task')
        bot.send_message(m.chat.id, '/continue для продолжения, \n'
                                    '/solve_task - для нового вопроса.', reply_markup=markup)
    else:
        logging.debug(f'Попытка обойти систему, пользователь {user}, id = {user_id}')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('/solve_task')
        bot.send_message(m.chat.id, 'Сначала задай вопрос с помощью команды /solve_task.', reply_markup=markup)


@bot.message_handler(commands=['debug'])
def logs(m):
    f = open('log_file.txt', 'r')
    try:
        bot.send_document(m.chat.id, f)
    except:
        logging.warning('Не удалось отправить документ с логами')
        bot.send_message(m.chat.id, 'Не удалось отправить документ с логами')
        if m.from_user.first_name != 'Alek':
            print('Функция /debug была использована сторонним пользователем.')
            logging.info('Команда /debug активирована')
    f.close()


@bot.message_handler(content_types=['text'])
def other(m):
    user_id = m.from_user.id
    user = m.from_user.first_name
    if type(m.from_user.last_name) is str:
        user += m.from_user.last_name
    logging.debug(f'Сработала функция сортировки простого текста, пользователь {user}, id = {user_id}.')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('/solve_task'))
    markup.add(KeyboardButton('/start'))
    bot.send_message(m.chat.id, 'Чтобы взаимодействовать со мной, используй команды '
                                '/solve_task \nили /start.', reply_markup=markup)


bot.infinity_polling()
