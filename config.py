BOT_TOKEN = '6058716388:AAGvTw8zqF3BXsFq6v4MywTtwhM9Fcnw2Rk' # Токен от Телеграмм бота
REST_API_TOKENS = ('61jf61LheMHsxVh8v4YhvvXiNSSdVamXBket6sBU', # Токен для доступа к API, tg бот
                   '1XYnMkfokzNQnY1iUfuDZ7w2FXGiyqsV2miTDbt2' # Запасной токен
                    )
NANONETS_API_TOKEN = 'bd609d8a-c631-11ed-9b9b-169ce9ee681d'


DEFAULT_IMG = 'img/gaduka-icon.png' # Изображение проекта по умолчанию
PORT = 80  # Не работает при запуске через Gunicorn
TIMEOUT_RUN_GADUKA = 10 # В секундах

CODE_RUN_API = 'http://127.0.0.1:80/'
# !!! Также нужно поменять в flask_site_host -> static -> code_page.js

API_SERVER = 'http://127.0.0.1:80/'
DIAMOND_GOOSE = 'http://127.0.0.1:80/'