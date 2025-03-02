from setuptools import setup, find_packages

setup(
    name='HabitNinja_Bot',  # Название вашего пакета
    version='0.1.2',  # Версия вашего пакета
    author='Han',  # Ваше имя
    author_email='Han@gmail.com',  # Ваш email
    description='Бот трекер привычек',  # Описание
    long_description=open('Readme.md').read(),  # Длинное описание (можно использовать README файл)
    long_description_content_type='text/markdown',  # Тип содержимого длинного описания
    url='https://github.com/Rapira16/HabitNinja_Bot',  # URL вашего проекта
    packages=find_packages(),  # Автоматически находит пакеты в проекте
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Минимальная версия Python
    install_requires=[  # Зависимости вашего проекта
        'certifi',
        'charset-normalizer',
        'idna',
        'pyTelegramBotAPI',
        'requests',
        'schedule',
        'telebot',
        'urllib3',
    ],
)