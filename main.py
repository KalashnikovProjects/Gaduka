""" Отсюда будут запускаться все остальные части проекта такие как:
API
Flask бекенд сайта
Телеграмм бот
"""
import os

from api import app

app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))