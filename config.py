import os

REST_API_TOKENS = (os.environ.get('REST_API_TOKENS1'), os.environ.get('REST_API_TOKENS2'))


DEFAULT_IMG = 'img/gaduka-icon.png' # Изображение проекта по умолчанию
PORT = 80  # Не работает при запуске через Gunicorn
TIMEOUT_RUN_GADUKA = 10  # В секундах
