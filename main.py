""" Отсюда будут запускаться все остальные части проекта такие как:
API
Flask бекенд сайта
Телеграмм бот
"""
import logging
from threading import Thread

from flask_site_host.flask_server import main
import time
import requests


def run():
    logging.info("Запущен пинг glitch хостингов")
    while True:
        requests.get("https://truth-chalk-servant.glitch.me")
        requests.get("https://gaduka.glitch.me")
        time.sleep(60)


if __name__ == '__main__':
    t = Thread(target=run)
    t.start()
    main()
