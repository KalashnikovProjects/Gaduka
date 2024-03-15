import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
REST_API_TOKENS = (os.environ.get('REST_API_TOKENS1'), os.environ.get('REST_API_TOKENS2'))
MYSQL_CONNECT_STRING = os.getenv("MYSQL")

DEFAULT_IMG = 'img/gaduka-icon.png'  # Изображение проекта по умолчанию
PORT = 10000
TIMEOUT_RUN_GADUKA = 10
