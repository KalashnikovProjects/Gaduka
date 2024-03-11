""" Отсюда будут запускаться все остальные части проекта такие как:
API
Flask бекенд сайта
Телеграмм бот
"""

from threading import Thread

import config
from flask_site_host.flask_server import main
import time
import requests


def run():
    while True:
        requests.get("https://truth-chalk-servant.glitch.me")
        requests.get("https://gaduka.glitch.me")
        time.sleep(60)


if __name__ == '__main__':
    t = Thread(target=run)
    t.start()
    main(port=config.PORT, host='0.0.0.0')
