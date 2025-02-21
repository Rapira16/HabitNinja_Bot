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
    # Устанавливаем соединение с базой данных 'habits.db'.
    # Если файл базы данных не существует, он будет создан.
    conn = sqlite3.connect('habits.db')

    # Создаем объект курсора для выполнения SQL-запросов.
    c = conn.cursor()

    # Создаем таблицу 'users', если она еще не существует.
    # Таблица содержит следующие поля:
    # - user_id: уникальный идентификатор пользователя (первичный ключ)
    # - name: имя пользователя
    # - motivation_time: время, когда пользователь получает мотивацию
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


#endregion