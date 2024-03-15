import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
REST_API_TOKENS = (os.environ.get('REST_API_TOKENS1'), os.environ.get('REST_API_TOKENS2'))

DEFAULT_IMG = 'img/gaduka-icon.png' # Изображение проекта по умолчанию
PORT = 80  # Не работает при запуске через Gunicorn
TIMEOUT_RUN_GADUKA = 10 # В секундах

CODE_RUN_API = 'http://127.0.0.1:80/'
# !!! Также нужно поменять в flask_site_host -> static -> code_page.js

API_SERVER = 'http://127.0.0.1:80/'
DIAMOND_GOOSE = 'http://127.0.0.1:80/'
