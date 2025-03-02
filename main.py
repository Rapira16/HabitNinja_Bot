import telebot
import sqlite3
from datetime import datetime
import schedule
import time
import threading
import random
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

bot = telebot.TeleBot("8094395413:AAGlIanHK3Ji99-N90Nkinvqk4ikRJlkeQg")

motivation = [
    "Верь в себя, и мир поверит в тебя."
    "Верь в себя, и мир поверит в тебя.",
    "Каждый день — новый шанс изменить свою жизнь.",
    "Успех — это результат упорства.",
    "Не бойся ошибок, бойся бездействия.",
    "Мечты становятся реальностью, когда ты действуешь.",
    "Начни с малого, но начинай.",
    "Трудности — это ступеньки к успеху.",
    "Ты сильнее, чем думаешь.",
    "Каждый шаг приближает к цели.",
    "Не останавливайся, пока не гордишься.",
    "Успех — это путь, а не пункт назначения.",
    "Делай то, что любишь, и не работай ни дня.",
    "Вдохновение приходит с действием.",
    "Сомнения убивают мечты.",
    "Будь смелым, и мир откроется перед тобой.",
    "Успех — это сумма мелких усилий.",
    "Не жди идеального момента, создавай его.",
    "Ты способен на большее, чем думаешь.",
    "Каждый день — это новая возможность.",
    "Действуй так, как будто уже успешен.",
    "Не сравнивай себя с другими, сравнивай себя с собой.",
    "Верь в процесс, и результаты придут.",
    "Упорство — ключ к успеху.",
    "Не позволяй страху остановить тебя.",
    "Твоя история только начинается.",
    "Ставь цели, и иди к ним.",
    "Каждый успех начинается с решения попробовать.",
    "Не бойся мечтать, бойся не пытаться.",
    "Ты — архитектор своей судьбы.",
    "Верь в свои силы, и они не подведут.",
    "Успех — это не случайность, а выбор.",
    "Делай шаги к своей мечте каждый день.",
    "Не позволяй неудачам определять тебя.",
    "Живи так, как будто уже достиг успеха.",
    "Твоя энергия привлекает твои возможности.",
    "Сложности — это временные преграды.",
    "Каждый день — это шанс стать лучше.",
    "Не останавливайся на достигнутом.",
    "Вдохновение — это результат действия.",
    "Ты можешь все, если веришь в себя.",
    "Успех приходит к тем, кто не сдается.",
    "Не бойся быть уникальным.",
    "Каждый момент — это возможность.",
    "Слушай свое сердце и действуй.",
    "Твоя решимость определяет твой успех.",
    "Не позволяй страху управлять твоей жизнью.",
    "Будь тем, кто вдохновляет других.",
    "Успех — это результат постоянства.",
    "Живи с намерением и страстью.",
    "Ты — творец своей судьбы."
]

intervals = {
    'min': 60,
    'h': 60 * 60,
    'hour': 60 * 60,
    'd': 60 * 60 * 24,
    'day': 60 * 60 * 24,
    'w': 60 * 60 * 24 * 30,
    'week': 60 * 60 * 24 * 7,
    'm': 60 * 60 * 24 * 30,
    'y': 60 * 60 * 24 * 30 * 12
}

# region Database Functions
def init_db():
    """
    Инициализирует базу данных 'habits.db'.

    Создает таблицы 'users', 'habits' и 'reminders', если они еще не существуют.
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  name TEXT,
                  motivation_time TEXT,
                  last_motivation INTEGER)''')

    c.execute('''CREATE TABLE IF NOT EXISTS habits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  habit_name TEXT,
                  created_date TEXT,
                  count INTEGER DEFAULT 0,
                  UNIQUE(user_id, habit_name))''')

    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  habit_id INTEGER,
                  reminder_time TEXT,
                  last_reminded INTEGER)''')

    conn.commit()
    conn.close()


def add_user(user_id, name, motivation_time=None):
    """
    Добавляет нового пользователя в базу данных.

    Args:
        user_id (int): Уникальный идентификатор пользователя.
        name (str): Имя пользователя.
        motivation_time (str, optional): Время, когда пользователь получает мотивацию. По умолчанию None.
    """
    last_motivation = 0

    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO users (user_id, name, motivation_time, last_motivation) VALUES (?, ?, ?, ?)",
              (user_id, name, motivation_time, last_motivation))

    conn.commit()
    conn.close()


def add_habit(user_id, habit_name):
    """
        Добавляет новую привычку в базу данных.

        Args:
            user_id (int): Уникальный идентификатор пользователя.
            habit_name (str): Название привычки.

        Returns:
            bool: True, если добавление прошло успешно, иначе False.
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        c.execute("INSERT INTO habits (user_id, habit_name, created_date) VALUES (?, ?, ?)",
                  (user_id, habit_name, created_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def add_reminder(user_id, habit_id, new_time):
    """
        Добавляет время для напоминания про привычку.

        Args:
            user_id (int): Уникальный идентификатор пользователя.
            habit_id (int): Идентефикационный номер привычки.
            new_time (str): Интервал для напоминания о привычке.

        Returns:
            bool: True, если добавление прошло успешно, иначе False.
    """
    last_reminded = 0

    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    try:
        c.execute("INSERT INTO reminders (user_id, habit_id, reminder_time, last_reminded) VALUES (?, ?, ?, ?)",
                  (user_id, habit_id, new_time, last_reminded))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def check_reminder(habit_id) -> bool:
    """
        Получает все привычки пользователя.

        Args:
            habit_id (int): Уникальный идентификатор привычки.

        Returns:
            bool: Если напоминание уже есть, то возвращает True, иначе False.
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute("SELECT reminder_time FROM reminders WHERE habit_id=?", (habit_id,))
    reminder = c.fetchone()

    if reminder is not None:
        return True
    return False


def get_user_habits(user_id):
    """
    Получает все привычки пользователя.

    Args:
        user_id (int): Уникальный идентификатор пользователя.

    Returns:
        list: Список привычек пользователя в виде кортежей (id, habit_name).
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute("SELECT id, habit_name FROM habits WHERE user_id=?", (user_id,))
    habits = c.fetchall()

    conn.close()
    return habits


def update_user_reminders(habit_id, new_time):
    """
        Обновляет данные о времени напоминания конкретной привычки.

        Args:
            habit_id (int): Идентефикатор конкретной привычки.
            new_time (str): Новое интервал для отображения напоминания о привычке.
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute(f"UPDATE reminders SET reminder_time = {new_time} WHERE habit_id=?", (habit_id,))

    conn.commit()
    conn.close()


def update_user_motivation(user_id, new_time):
    """
        Обновляет интервал для рассылки мотивационных сообщений для пользователя.

        Args:
            user_id (int): Уникальный идентификатор пользователя.
            new_time (str): Название привычки.
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute("UPDATE users SET motivation_time = ? WHERE user_id = ?", (new_time, user_id))

    conn.commit()
    conn.close()


def update_habit_count(habit_id):
    """
    Увеличивает счетчик выполнения привычки на 1.

    Args:
        habit_id (int): Уникальный идентификатор привычки.
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute("UPDATE habits SET count = count + 1 WHERE id=?", (habit_id,))
    conn.commit()
    conn.close()


def get_stats(user_id):
    """
    Получает статистику привычек пользователя.

    Args:
        user_id (int): Уникальный идентификатор пользователя.

    Returns:
        list: Список статистики привычек пользователя в виде кортежей (habit_name, count).
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute("SELECT habit_name, count FROM habits WHERE user_id=?", (user_id,))
    stats = c.fetchall()

    conn.close()
    return stats


def delete_habit(habit_id):
    """
    Удаляет привычку из базы данных.

    Args:
        habit_id (int): Уникальный идентификатор привычки.
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute("DELETE FROM habits WHERE id=?", (habit_id,))
    conn.commit()
    conn.close()


def update_habit_name(habit_id, new_name):
    """
    Обновляет название привычки в базе данных.

    Args:
        habit_id (int): Уникальный идентификатор привычки.
        new_name (str): Новое название привычки.
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute("UPDATE habits SET habit_name=? WHERE id=?", (new_name, habit_id))
    conn.commit()
    conn.close()
# endregion

# region Menu & Handlers
def create_menu():
    """
    Создает и возвращает меню с кнопками для взаимодействия с пользователем.

    Returns:
        ReplyKeyboardMarkup: Меню с кнопками для добавления, редактирования, удаления привычек,
        отметки выполнения, просмотра статистики, установки напоминаний и мотивационных сообщений.
    """
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(KeyboardButton("Добавить привычку ➕"))
    menu.add(KeyboardButton("Отметить выполнение ✅"))
    menu.add(KeyboardButton("Статистика 📊"))
    menu.add(KeyboardButton("Удалить привычку ❌"))
    menu.add(KeyboardButton("Редактировать привычку ✏️"))
    menu.add(KeyboardButton("Установить напоминание ⏰"))
    menu.add(KeyboardButton("Установить мотивационное сообщение 💪🏻"))
    return menu

@bot.message_handler(commands=['start'])
def start(message):
    """
    Обрабатывает команду /start. Приветствует пользователя и отправляет меню для управления привычками.

    Args:
        message (types.Message): Объект сообщения от пользователя.
    """
    user = message.chat
    add_user(user.id, user.first_name)
    bot.send_message(
        message.chat.id,
        f"👋 Привет {user.first_name}! Я помогу тебе отслеживать привычки!\n\n"
        "Используй кнопки ниже для управления:",
        reply_markup=create_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """
    Обрабатывает текстовые сообщения от пользователя и вызывает соответствующие функции
    в зависимости от текста сообщения.

    Args:
        message (types.Message): Объект сообщения от пользователя.
    """
    if message.text == "Добавить привычку ➕":
        add_habit_start(message)
    elif message.text == "Отметить выполнение ✅":
        track_habit(message)
    elif message.text == "Статистика 📊":
        show_stats(message)
    elif message.text == "Удалить привычку ❌":
        delete_habit_start(message)
    elif message.text == "Редактировать привычку ✏️":
        edit_habit_start(message)
    elif message.text == "Установить напоминание ⏰":
        schedule_reminder_start(message)
    elif message.text == "Установить мотивационное сообщение 💪🏻":
        schedule_motivation_start(message)
    elif message.text == "Назад":
        bot.send_message(
            message.chat.id,
            "Команда отменена.",
            reply_markup=create_menu()
        )
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ Используй кнопки ниже ⬇️",
            reply_markup=create_menu()
        )

# region Habit Management
@bot.message_handler(commands=['add_habit'])
def add_habit_start(message):
    """
    Запрашивает у пользователя название новой привычки.

    Args:
        message (types.Message): Объект сообщения от пользователя.
    """
    msg = bot.send_message(
        message.chat.id,
        "➕ Введите название новой привычки:",
        reply_markup=ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, add_habit_end)

def add_habit_end(message):
    """
    Обрабатывает введенное пользователем название привычки и добавляет её в список.

    Args:
        message (types.Message): Объект сообщения от пользователя с названием привычки.
    """
    user_id = message.from_user.id
    habit_name = message.text.strip()

    if len(habit_name) < 2:
        bot.send_message(
            message.chat.id,
            "❌ Название должно быть не короче 2 символов!",
            reply_markup=create_menu()
        )
        return

    if add_habit(user_id, habit_name):
        bot.send_message(
            message.chat.id,
            f"✅ Привычка '{habit_name}' успешно добавлена!",
            reply_markup=create_menu()
        )
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Привычка '{habit_name}' уже существует!",
            reply_markup=create_menu()
        )

@bot.message_handler(commands=['track_habit'])
def track_habit(message):
    """
    Отображает список привычек пользователя для отметки выполнения.

    Если у пользователя нет привычек, отправляет сообщение об этом.

    Args:
        message (types.Message): Объект сообщения от пользователя.
    """
    user_id = message.from_user.id
    habits = get_user_habits(user_id)

    if not habits:
        bot.send_message(
            message.chat.id,
            "❌ У вас нет добавленных привычек.",
            reply_markup=create_menu()
        )
        return

    keyboard = InlineKeyboardMarkup()
    for habit in habits:
        habit_id, habit_name = habit
        keyboard.add(InlineKeyboardButton(
            text=f"✅ {habit_name}",
            callback_data=f"track_{habit_id}"
        ))
    keyboard.add(InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu"))

    bot.send_message(
        message.chat.id,
        "📅 Выберите привычку для отметки:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("track_"))
def track_habit_complete(call):
    """
    Обрабатывает callback-запрос для отметки выполнения привычки.

    Args:
        call (types.CallbackQuery): Объект callback-запроса от пользователя.
    """
    habit_id = call.data.split("_")[1]

    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT habit_name FROM habits WHERE id=?", (habit_id,))
    habit_name = c.fetchone()[0]
    conn.close()

    update_habit_count(habit_id)

    bot.answer_callback_query(call.id, f"✅ Привычка '{habit_name}' отмечена!")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🎉 Привычка '{habit_name}' успешно отмечена!"
    )
    bot.send_message(
        call.message.chat.id,
        "🏠 Возвращаемся в главное меню:",
        reply_markup=create_menu()
    )

@bot.message_handler(commands=['stats'])
def show_stats(message):
    """
    Отображает статистику выполнения привычек пользователя.

    Если статистика отсутствует, отправляет сообщение об этом.

    Args:
        message (types.Message): Объект сообщения от пользователя.
    """
    user_id = message.from_user.id
    stats = get_stats(user_id)

    if not stats:
        bot.send_message(
            message.chat.id,
            "📊 Статистика пока пуста.",
            reply_markup=create_menu()
        )
        return

    message_text = "📊 Ваша статистика:\n\n" + "\n".join(
        [f"• {habit[0]}: {habit[1]} раз" for habit in stats]
    )

    bot.send_message(
        message.chat.id,
        message_text,
        reply_markup=create_menu()
    )

# region Delete Habit
@bot.message_handler(commands=['delete_habit'])
def delete_habit_start(message):
    """
    Отображает список привычек пользователя для удаления.

    Если у пользователя нет привычек, отправляет сообщение об этом.

    Args:
        message (types.Message): Объект сообщения от пользователя.
    """
    user_id = message.from_user.id
    habits = get_user_habits(user_id)

    if not habits:
        bot.send_message(
            message.chat.id,
            "❌ У вас нет добавленных привычек.",
            reply_markup=create_menu()
        )
        return

    keyboard = InlineKeyboardMarkup()
    for habit in habits:
        habit_id, habit_name = habit
        keyboard.add(InlineKeyboardButton(
            text=f"❌ {habit_name}",
            callback_data=f"delete_{habit_id}"
        ))
    keyboard.add(InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu"))

    bot.send_message(
        message.chat.id,
        "🗑️ Выберите привычку для удаления:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def delete_habit_complete(call):
    """
    Обрабатывает callback-запрос для удаления привычки.

    Args:
        call (types.CallbackQuery): Объект callback-запроса от пользователя.
    """
    habit_id = call.data.split("_")[1]

    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT habit_name FROM habits WHERE id=?", (habit_id,))
    habit_name = c.fetchone()[0]
    conn.close()

    delete_habit(habit_id)

    bot.answer_callback_query(call.id, f"❌ Привычка '{habit_name}' удалена!")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🗑️ Привычка '{habit_name}' успешно удалена!"
    )
    bot.send_message(
        call.message.chat.id,
        "🏠 Возвращаемся в главное меню:",
        reply_markup=create_menu()
    )

# region Edit Habit
@bot.message_handler(commands=['edit_habit'])
def edit_habit_start(message):
    """
    Отображает список привычек пользователя для редактирования.

    Если у пользователя нет привычек, отправляет сообщение об этом.

    Args:
        message (types.Message): Объект сообщения от пользователя.
    """
    user_id = message.from_user.id
    habits = get_user_habits(user_id)

    if not habits:
        bot.send_message(
            message.chat.id,
            "❌ У вас нет добавленных привычек.",
            reply_markup=create_menu()
        )
        return

    keyboard = InlineKeyboardMarkup()
    for habit in habits:
        habit_id, habit_name = habit
        keyboard.add(InlineKeyboardButton(
            text=f"✏️ {habit_name}",
            callback_data=f"edit_{habit_id}"
        ))
    keyboard.add(InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu"))

    bot.send_message(
        message.chat.id,
        "✏️ Выберите привычку для редактирования:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def edit_habit_complete(call):
    """
    Обрабатывает callback-запрос для редактирования привычки.
    Запрашивает у пользователя новое название привычки.

    Args:
        call (types.CallbackQuery): Объект callback-запроса от пользователя.
    """
    habit_id = call.data.split("_")[1]

    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT habit_name FROM habits WHERE id=?", (habit_id,))
    habit_name = c.fetchone()[0]
    conn.close()

    msg = bot.send_message(
        call.message.chat.id,
        f"🔄 Введите новое название для привычки '{habit_name}':",
        reply_markup=ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(
        msg,
        lambda message, h_id=habit_id: update_habit_end(message, h_id)
    )

def update_habit_end(message, habit_id):
    """
    Обновляет название привычки на основе введенного пользователем текста.

    Если новое название короче 2 символов, отправляет сообщение об ошибке.

    Args:
        message (types.Message): Объект сообщения от пользователя с новым названием привычки.
        habit_id (int): Идентификатор привычки, которую нужно обновить.
    """
    new_name = message.text.strip()

    if len(new_name) < 2:
        bot.send_message(
            message.chat.id,
            "❌ Название должно быть не короче 2 символов!",
            reply_markup=create_menu()
        )
        return

    update_habit_name(habit_id, new_name)

    bot.send_message(
        message.chat.id,
        f"✅ Название привычки успешно обновлено на '{new_name}'!",
        reply_markup=create_menu()
    )

# region Reminders
@bot.message_handler(commands=['schedule_reminder'])
def schedule_reminder_start(message):
    """
        Отображает список привычек пользователя для редактирования напоминаний о них.

        Если у пользователя нет привычек, отправляет сообщение об этом.

        Args:
            message (types.Message): Объект сообщения от пользователя.
    """
    user_id = message.from_user.id
    habits = get_user_habits(user_id)

    if not habits:
        bot.send_message(
            message.chat.id,
            "❌ У вас нет добавленных привычек.",
            reply_markup=create_menu()
        )
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for habit in habits:
        habit_id, habit_name = habit
        keyboard.add(InlineKeyboardButton(
            text=f"✏️ {habit_name}",
            callback_data=f"reminder1_{habit_id}"
        ))
    keyboard.add(InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu"))

    bot.send_message(
        message.chat.id,
        "⏰️ Выберите привычку для установки напоминания:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("reminder1_"))
def schedule_reminder_middle(call):
    """
        Обрабатывает callback-запрос для редактирования напоминания о привычке.
        Запрашивает у пользователя новый интервал для привычки.

        Args:
            call (types.CallbackQuery): Объект callback-запроса от пользователя.
    """
    habit_id = call.data.split('_')[1]

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="⏰ Раз в час", callback_data=f"reminder2_h_{habit_id}"))
    keyboard.add(InlineKeyboardButton(text="⏰ Раз в день", callback_data=f"reminder2_d_{habit_id}"))
    keyboard.add(InlineKeyboardButton(text="⏰ Раз в неделю", callback_data=f"reminder2_w_{habit_id}"))
    keyboard.add(InlineKeyboardButton(text="⏰ Раз в месяц", callback_data=f"reminder2_m_{habit_id}"))
    keyboard.add(InlineKeyboardButton(text="⏰ Раз в год", callback_data=f"reminder2_y_{habit_id}"))

    keyboard.add(InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu"))

    bot.send_message(
        call.message.chat.id,
        "⏰️ Выберите интервал, с которым вы хотите получать напоминания:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("reminder2_"))
def schedule_reminder_end(call):
    """
        Обрабатывает callback-запрос для редактирования напоминания о привычке.
        Подтверждает ответ пользователя и отпраляет запрос в БД на обновление интервала.

        Args:
            call (types.CallbackQuery): Объект callback-запроса от пользователя.
    """
    interval, habit_id = call.data.split('_')[1:]

    if check_reminder(habit_id):
        update_user_reminders(habit_id, interval)
    else:
        user = call.message.chat
        add_reminder(user.id, habit_id, interval)

    bot.send_message(
        call.message.chat.id,
        "⏰️ Новый интервал установлен!",
        reply_markup=create_menu()
    )

def send_reminder(user_id, habit_id):
    """
        Отправляет напоминания о выполнении привычки пользователю.

        Args:
            user_id (int): Уникальный идентефикатор пользователя.
            habit_id (int): Идентефикатор конкретной привычки.
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute("SELECT habit_name FROM habits WHERE habit_id=?", (habit_id,))
    habit_name = c.fetchone()

    conn.close()

    bot.send_message(
        user_id,
        text=f"⏰ Напоминание, что вам пора {habit_name}!"
    )

# region Motivation
@bot.message_handler(commands=['schedule_motivation'])
def schedule_motivation_start(message):
    """
        Спрашивает у пользователя, как часто он хочет получать мотивационные сообщения от бота.

        Args:
            message (types.Message): Объект сообщения от пользователя.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(InlineKeyboardButton(text="💪🏻💪🏻💪🏻 ОЧЕНЬ много (ежеминутно)", callback_data="motiv_min"))
    keyboard.add(InlineKeyboardButton(text="💪🏻💪🏻 Много (каждый час)", callback_data="motiv_hour"))
    keyboard.add(InlineKeyboardButton(text="💪🏻 Немного (каджый день)", callback_data="motiv_day"))
    keyboard.add(InlineKeyboardButton(text=" Мало (каджую неделю)", callback_data="motiv_week"))
    keyboard.add(InlineKeyboardButton(text="-💪🏻 Совсем мало (каджый месяц)", callback_data="motiv_month"))

    bot.send_message(
        message.chat.id,
        "💪🏻 Сколько мотивации ты хочешь???",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("motiv_"))
def schedule_motivation_end(call):
    """
        Обрабатывает callback-запрос для редактирования интервала для мотивационных сообщений.

        Args:
            call (types.CallbackQuery): Объект callback-запроса от пользователя.
    """
    user_id = call.message.chat.id
    interval = call.data.split('_')[1]

    update_user_motivation(user_id, interval)

    bot.send_message(
        call.message.chat.id,
        "️💪🏻 Новый интервал для мотивации установлен!",
        reply_markup=create_menu()
    )

def send_motivation(user_id):
    """
        Отправляет мотивационные сообщения пользователю.

        Args:
            user_id (int): Уникальный идентефикатор пользователя.
    """
    quote = random.choice(motivation)

    bot.send_message(
        user_id,
        text=quote
    )

# endregion

def run_scheduler():
    """
        Проверяет, не пора ли оправлять напоминания и мотивацию.
    """
    fl = True

    while True:
        conn = sqlite3.connect('habits.db')
        c = conn.cursor()

        c.execute("SELECT user_id, habit_id, reminder_time, last_reminded FROM reminders")
        reminders = c.fetchall()
        c.execute("SELECT user_id, motivation_time, last_motivation FROM users")
        motivations = c.fetchall()

        for rem in reminders:
            if rem[3] + intervals[rem[2]] >= time.time():
                send_reminder(rem[0], rem[1])
                c.execute(f"UPDATE reminders SET last_reminded = {time.time()} WHERE habit_id=?",
                          (rem[1],))

        for motiv in motivations:
            if motiv[2] + intervals[motiv[1]] >= time.time():
                send_motivation(motiv[0])
                c.execute(f"UPDATE users SET last_motivation = {time.time()} WHERE user_id=?",
                          (motiv[0],))

        conn.commit()
        conn.close()





# region Back to Menu
@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_to_menu(call):
    """
    Возвращает пользователя в главное меню, удаляя предыдущее сообщение.

    Args:
        call (types.CallbackQuery): Объект callback-запроса от пользователя.
    """
    bot.send_message(
        chat_id=call.message.chat.id,
        text="🏠 Возвращаемся в главное меню:",
        reply_markup=create_menu()
    )
    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

# endregion

if __name__ == "__main__":
    init_db()
    print("🚀 Бот успешно запущен!")

    # Запуск планировщика в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True  # Установите поток как демон, чтобы он завершался при завершении основного потока
    scheduler_thread.start()

    bot.polling(none_stop=True)