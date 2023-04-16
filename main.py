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

"""