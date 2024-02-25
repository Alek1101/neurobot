import telebot
from API_TOKEN import TOKEN
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot(TOKEN)

check = False


@bot.message_handler(commands=['start'])
def start(m):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('/solve_task'))
    bot.send_message(m.chat.id, 'Привет! Я - Telegram-бот с подключённой нейросетью, созданный, чтобы отвечать'
                                ' на твои вопросы. Задавай мне вопросы на тему программирования, и я постараюсь '
                                'качественно '
                                'на них ответить.')
    bot.send_message(m.chat.id, 'Для того, чтобы задать вопрос, используй команду /solve_task.', reply_markup=markup)


@bot.message_handler(commands=['solve_task'])
def instruction(m):
    bot.send_message(m.chat.id, 'Я отвечаю на вопросы на тему программирования, \nнапиши свой вопрос кратко '
                                'и точно и укажи язык программирования, о котором идёт речь, '
                                '\nа также язык, на котором '
                                ' мне следует тебе ответить.')
    bot.send_message(m.chat.id, 'Следующим сообщением отправь свой вопрос.')
    bot.register_next_step_handler(m, question_treatment)


def question_treatment(m):
    global check
    check = False
    user_id = m.from_user.id
    if m.content_type != 'text':
        bot.send_message(user_id, text='Отправь промт текстовым сообщением')
        bot.register_next_step_handler(m, question_treatment)
        return
    if m.text == '/continue' or m.text == '/solve_task':
        bot.send_message(m.chat.id, 'Сначала задай свой вопрос.')
        bot.register_next_step_handler(m, question_treatment)
        return
    user_prompt = m.text
    bot.send_message(m.chat.id, 'Промт принят!')
    check = True
    # bot.send_chat_action(m.chat.id, 'typing')
    # Сообщение от GPT
    #     bot.send_message(m.chat.id, '')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('/continue', '/solve_task')
    bot.send_message(m.chat.id, '/continue для более подробного ответа, \n'
                                '/solve_task - для нового вопроса.', reply_markup=markup)


@bot.message_handler(commands=['continue'])
def question_continuation(m):
    if check:
        bot.send_message(m.chat.id, '"')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('/continue', '/solve_task')
        bot.send_message(m.chat.id, '/continue для более подробного ответа, \n'
                                    '/solve_task - для нового вопроса.', reply_markup=markup)
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('/solve_task')
        bot.send_message(m.chat.id, 'Сначала задай вопрос с помощью команды /solve_task.', reply_markup=markup)


#     Продолжение ответа


bot.polling()
