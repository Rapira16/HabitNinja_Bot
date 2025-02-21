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

    # Создаем таблицу 'habits', если она еще не существует.
    # Таблица содержит следующие поля:
    # - id: уникальный идентификатор привычки (первичный ключ, автоинкремент)
    # - user_id: идентификатор пользователя, которому принадлежит привычка
    # - habit_name: название привычки
    # - created_date: дата создания привычки
    # - count: количество выполнений привычки (по умолчанию 0)
    # Уникальное ограничение на сочетание user_id и habit_name, чтобы избежать дублирования привычек для одного пользователя.
    c.execute('''CREATE TABLE IF NOT EXISTS habits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  habit_name TEXT,
                  created_date TEXT,
                  count INTEGER DEFAULT 0,
                  UNIQUE(user_id, habit_name))''')

    # Создаем таблицу 'reminders', если она еще не существует.
    # Таблица содержит следующие поля:
    # - id: уникальный идентификатор напоминания (первичный ключ, автоинкремент)
    # - user_id: идентификатор пользователя, которому принадлежит напоминание
    # - habit_id: идентификатор привычки, для которой установлено напоминание
    # - reminder_time: время, когда должно быть отправлено напоминание
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  habit_id INTEGER,
                  reminder_time TEXT)''')

    # Сохраняем изменения в базе данных.
    conn.commit()

    # Закрываем соединение с базой данных.
    conn.close()


def add_user(user_id, name, motivation_time=None):
    # Устанавливаем соединение с базой данных 'habits.db'.
    conn = sqlite3.connect('habits.db')

    # Создаем объект курсора для выполнения SQL-запросов.
    c = conn.cursor()

#endregion