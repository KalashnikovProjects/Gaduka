import os

REST_API_TOKENS = (os.environ['API_KEY1'], # Токен для доступа к API, tg бот
                   os.environ['API_KEY2'])
database_server = "http://127.0.0.1:80"

DEFAULT_IMG = 'img/gaduka-icon.png' # Изображение проекта по умолчанию
PORT = 80  # Не работает при запуске через Gunicorn