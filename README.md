Полностью автономная версия с базой данной **SQLite**, на захощеном сайте используется **MySQL**.

Используется только для проверки.
____

Этот код будет работать полностью локально, но с ограничениями телеграмма:

* При запуске кода будет telegram.error.Conflict
из за того, что бот также запущен на хосте.

* На сайте не будет работать кнопка регистрации (на локалхосте, на обычном будет)

Проблема связанна с тем, что [Telegram Login Widget](https://core.telegram.org/widgets/login)
может работать только на 1 домене (https://gaduka.sytes.net/).

На время проверки я могу перепривязать его к домену ngrok, это делается через BotFather.

Для полноценного хоста проекта используется 3 ветки и 4 хостинга:
[hosting/Glitch](https://github.com/KalashnikovProjects/WebProject/tree/hosting/Glitch) - хостинг Glitch, API запуска кода

[hosting/Glitch-Гадюкабот](https://github.com/KalashnikovProjects/WebProject/tree/hosting/Glitch-%D0%93%D0%B0%D0%B4%D1%8E%D0%BA%D0%B0%D0%B1%D0%BE%D1%82) - хостинг Glitch, на нём работает ТГ бот

[hosting/Render](https://github.com/KalashnikovProjects/WebProject/tree/hosting/Render) - хостинг Render, весь основной Flask, API бд
Хостинг для базы данных MySQL (на 5 гб) - [Planet Scale](https://planetscale.com/), есть проблемы с работой в России