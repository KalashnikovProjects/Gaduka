""" Отсюда будут запускаться все остальные части проекта такие как:
API
Flask бекенд сайта
Телеграмм бот
"""

from flask_site_host.flask_server import main

if __name__ == '__main__':
    app = main()