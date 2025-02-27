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


# region Database Functions
def init_db():
    """
    Инициализирует базу данных 'habits.db'.

    Создает таблицы 'users', 'habits' и 'reminders', если они еще не существуют.
    """
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, name TEXT, motivation_time TEXT)''')

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
                  reminder_time TEXT)''')

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
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO users (user_id, name, motivation_time) VALUES (?, ?, ?)",
              (user_id, name, motivation_time))

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
    menu.add(KeyboardButton("Установить мотивационное сообщение ⏰"))
    return menu

@bot.message_handler(commands=['start'])
def start(message):
    """
    Обрабатывает команду /start. Приветствует пользователя и отправляет меню для управления привычками.

    Args:
        message (types.Message): Объект сообщения от пользователя.
    """
    user = message.from_user
    add_user(user.id, user.first_name)
    bot.send_message(
        message.chat.id,
        f"👋 Привет {user.first_name}! Я помогу тебе отслеживать привычки!\n\n"
        "Используй кнопки ниже для управления:",
        reply_markup=create_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "Добавить привычку ➕":
        add_habit_start(message)

# region Habit Management
@bot.message_handler(commands=['add_habit'])
def add_habit_start(message):
    msg = bot.send_message(message.chat.id, "New", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, add_habit_end)

def add_habit_end(message):
    user_id = message.from_user.id
    habit_name = message.text.strip()

    if len(habit_name) < 2:
        bot.send_message(message.chat.id, "Short name", reply_markup=create_menu())
        return

# endregion