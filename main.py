""" Отсюда будут запускаться все остальные части проекта такие как:
API
Flask бекенд сайта
Телеграмм бот
"""
from multiprocessing import Process

from flask_site_host import flask_server
from tg_bot import tg_main


if __name__ == "__main__":
    p1 = Process(target=tg_main.main)
    p1.start()
    p2 = Process(target=flask_server.main)
    p2.start()
    p1.join()
    p2.join()

"""
Полностью автономная версия с базой данной SQLite,

Этот код будет не полностью работать локально из за ограничений телеграмма
1 При запуске кода будет telegram.error.Conflict
Из за того, что бот также запущен на хосте

2 На сайте не будет работать кнопка регистрации (на локалхосте, на обычном будет)
Проблема связанна с тем, что Telegram Login Widget https://core.telegram.org/widgets/login
может работать только на 1 домене (у нас это https://gaduka.sytes.net/).
На время проверки я могу перепривязать его к домену ngrok, это делается через BotFather
"""