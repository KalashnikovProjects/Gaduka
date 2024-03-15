from flask import Flask
from threading import Thread
import os

app = Flask('')


@app.route('/')
def home():
    return "I'm alive"


def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


def keep_alive():
    t = Thread(target=run)
    t.start()

# Поставил 2 UptimeRobot'а каждые 5 минут на сайт проекта Glitch,
# в Glitch если нет запросов в течение 5 минут проект засыпает
