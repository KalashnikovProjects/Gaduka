# [<img src="https://github.com/KalashnikovProjects/Gaduka/raw/main/flask_site_host/static/img/gaduka-icon.png" width="50"/>](flask_site_host/static/img/gaduka-icon.png) Язык программирования «Гадюка»

## - это язык программирования на русском языке, рассчитанный на учеников средней и старшей школы, представленный в виде сайта https://gaduka.sytes.net/ и документации https://gaduka-docs.readthedocs.io/

[<img src="https://github.com/KalashnikovProjects/Gaduka/raw/main/gaduka-main.png" width="300"/>](flask_site_host/static/img/gaduka-main.png) 

[<img src="https://github.com/KalashnikovProjects/Gaduka/raw/main/gaduka-code.png" width="300"/>](flask_site_host/static/img/gaduka-code.png) 

В ветке main полностью автономная версия с базой данной **SQLite**, она используется только для теста.

### Сам проект сейчас использует 5 хостингов:

* [hosting/Glitch](https://github.com/KalashnikovProjects/WebProject/tree/hosting/Glitch) - Код из этой ветки хостится на glitch.com, обрабатывает API запросы на выполнение кода на Гадюке

* [hosting/Glitch-Гадюкабот](https://github.com/KalashnikovProjects/WebProject/tree/hosting/Glitch-%D0%93%D0%B0%D0%B4%D1%8E%D0%BA%D0%B0%D0%B1%D0%BE%D1%82) -  Хостится на Glitch, хостит tg бота (эту часть проекта делал [**estestvenno**](https://github.com/estestvenno))

* [hosting/Render](https://github.com/KalashnikovProjects/WebProject/tree/hosting/Render) - хостинг Render, хостит основу сайта и API для работы с базой данных.

* Хостинг для базы данных MySQL - сейчас это alwaysdata.com

* Хостинг для [документации](https://gaduka-docs.readthedocs.io/) - https://readthedocs.org/

  >  Хостинги выбирались среди бесплатных, поэтому в этих ветках есть немало костылей для запуска кода в неподходящем для этого месте.

### Для работы в зависимости от ветки могут понадобиться следующие переменные окружения:
* `BOT_TOKEN` - токен телеграмм бота
* `REST_API_TOKENS1` и `REST_API_TOKENS2` - токены для доступа к API базы данных, задаются на сервере базы данных этими же переменными окружения.
* `MYSQL` - строка *MySQL*
