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

    # Выполняем SQL-запрос для добавления нового пользователя в таблицу 'users'.
    # Используем 'INSERT OR IGNORE', чтобы избежать добавления дубликатов
    # (если пользователь с таким user_id уже существует, запрос не выполнится).
    # Параметры передаются через кортеж, чтобы избежать SQL-инъекций.
    c.execute("INSERT OR IGNORE INTO users (user_id, name, motivation_time) VALUES (?, ?, ?)",
              (user_id, name, motivation_time))

    # Сохраняем изменения в базе данных.
    conn.commit()

    # Закрываем соединение с базой данных.
    conn.close()

    
def add_habit(user_id, habit_name):
    # Устанавливаем соединение с базой данных 'habits.db'.
    conn = sqlite3.connect('habits.db')

    # Создаем объект курсора для выполнения SQL-запросов.
    c = conn.cursor()

    # Получаем текущую дату и время в формате "YYYY-MM-DD HH:MM:SS".
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Выполняем SQL-запрос для добавления новой привычки в таблицу 'habits'.
        # Параметры передаются через кортеж, чтобы избежать SQL-инъекций.
        c.execute("INSERT INTO habits (user_id, habit_name, created_date) VALUES (?, ?, ?)",
                  (user_id, habit_name, created_date))

        # Сохраняем изменения в базе данных.
        conn.commit()

        # Возвращаем True, если добавление прошло успешно.
        return True
    except sqlite3.IntegrityError:
        # Если возникла ошибка целостности (например, дублирование уникального значения),
        # возвращаем False.
        return False
    finally:
        # Закрываем соединение с базой данных в любом случае (успех или ошибка).
        conn.close()


def get_user_habits(user_id):
    # Устанавливаем соединение с базой данных 'habits.db'.
    conn = sqlite3.connect('habits.db')

    # Создаем объект курсора для выполнения SQL-запросов.
    c = conn.cursor()

    # Выполняем SQL-запрос для получения всех привычек пользователя по его user_id.
    # Запрос выбирает id и habit_name из таблицы 'habits', где user_id соответствует переданному значению.
    c.execute("SELECT id, habit_name FROM habits WHERE user_id=?", (user_id))

    # Извлекаем все результаты запроса и сохраняем их в переменной habits.
    # Результат будет списком кортежей, где каждый кортеж представляет одну привычку.
    habits = c.fetchall()

    # Закрываем соединение с базой данных.
    conn.close()

    # Возвращаем список привычек пользователя.
    return habits


def update_habit_count(habit_id):
    # Устанавливаем соединение с базой данных 'habits.db'.
    conn = sqlite3.connect('habits.db')

    # Создаем объект курсора для выполнения SQL-запросов.
    c = conn.cursor()

    # Выполняем SQL-запрос для обновления счетчика привычки.
    # Увеличиваем значение поля 'count' на 1 для привычки с указанным habit_id.
    c.execute("UPDATE habits SET count = count + 1 WHERE id=?", (habit_id, ))

    # Сохраняем изменения в базе данных.
    conn.commit()

    # Закрываем соединение с базой данных.
    conn.close()


def get_stats(user_id):
    # Устанавливаем соединение с базой данных 'habits.db'.
    conn = sqlite3.connect('habits.db')

    # Создаем объект курсора для выполнения SQL-запросов.
    c = conn.cursor()

    # Выполняем SQL-запрос для получения статистики привычек пользователя по его user_id.
    # Запрос выбирает habit_name и count из таблицы 'habits', где user_id соответствует переданному значению.
    c.execute("SELECT habit_name, count FROM habits WHERE user_id=?", (user_id,))

    # Извлекаем все результаты запроса и сохраняем их в переменной stats.
    # Результат будет списком кортежей, где каждый кортеж содержит название привычки и ее счетчик.
    stats = c.fetchall()

#endregion