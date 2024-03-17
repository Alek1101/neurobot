import sqlite3


def execute_query(sql_query, data=None):
    connection = sqlite3.connect('project_2.db')
    cursor = connection.cursor()
    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)

    connection.commit()
    connection.close()


def execute_selection_query(sql_query, data=None):
    connection = sqlite3.connect('project_2.db')
    cursor = connection.cursor()

    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)
    rows = cursor.fetchone()
    connection.close()
    return rows


def create_table():
    sql_query = f'CREATE TABLE IF NOT EXISTS users ' \
                f'(id INTEGER PRIMARY KEY, ' \
                f'user_id INTEGER, ' \
                f'language TEXT, ' \
                f'level TEXT, ' \
                f'task TEXT, ' \
                f'answer TEXT)'
    execute_query(sql_query)


def clean_table():
    # TODO: Требуется написать код для удаления всех записей таблицы
    sql = 'DELETE FROM users'
    execute_query(sql)


def insert_row(values):
    # TODO: Требуется написать код для вставки новой строки в таблицу
    data = values
    sql = f'INSERT INTO users (user_id, language, level, task, answer) VALUES (?, ?, ?, ?, ?);'
    execute_query(sql, data)


def delete_data(user_id: int):
    sql = f'DELETE FROM users WHERE user_id = {user_id}'
    execute_query(sql)


def is_value_in_table(column_name, value):
    # TODO: Требуется написать код для проверки есть ли запись в таблице
    # Создаёт запрос SELECT колонка FROM имя_таблицы WHERE колонка == значение LIMIT 1
    sql = f'SELECT {column_name} FROM users WHERE {column_name}="{value}" LIMIT 1'
    execute_selection_query(sql)


def get_data_for_user(user_id):
    # TODO: Здесь вам нужно добавить код для выполнения запроса и записи в логи
    sql = f'SELECT * FROM users WHERE user_id={user_id};'
    return execute_selection_query(sql)


def update_data(user_id: int, column: str, new_value: str):
    sql = f'UPDATE users SET {column} = "{new_value}" WHERE user_id = {user_id}'
    execute_query(sql)


print(get_data_for_user(5156336478))