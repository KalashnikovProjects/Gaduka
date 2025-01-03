import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
REST_API_TOKENS = (os.environ.get('REST_API_TOKENS1'), os.environ.get('REST_API_TOKENS2'))

CODE_RUN_API = os.environ.get('CODE_RUN_API', "http://127.0.0.1:80/")
MAIN_API = os.environ.get('MAIN_API', "http://127.0.0.1:80/")
