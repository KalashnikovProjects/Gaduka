import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_BOT_NAME = os.environ.get('TELEGRAM_BOT_NAME')
REST_API_TOKENS = os.environ.get('REST_API_TOKENS1'), os.environ.get('REST_API_TOKENS2')
POSTGRES_CONNECT_STRING = os.environ.get("POSTGRES_CONNECT_STRING")
if not POSTGRES_CONNECT_STRING:
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost:80")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_CONNECT_STRING = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

DEFAULT_IMG = "img/gaduka-icon.png"  # Изображение проекта по умолчанию
FLASK_SERVER_PORT = os.environ.get('FLASK_SERVER_PORT', 8080)

CODE_RUN_API = os.environ.get('CODE_RUN_API', "http://localhost/")
