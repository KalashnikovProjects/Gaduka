import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
REST_API_TOKENS = (os.environ.get('REST_API_TOKENS1'), os.environ.get('REST_API_TOKENS2'))
POSTGRES_CONNECT_STRING = os.environ.get("POSTGRES_CONNECT_STRING")
if not POSTGRES_CONNECT_STRING:
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost:80")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_CONNECT_STRING = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

DEFAULT_IMG = 'img/gaduka-icon.png'  # Изображение проекта по умолчанию
PORT = 10000
