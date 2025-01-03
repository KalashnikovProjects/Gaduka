import base64
from telegram import InputFile, Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from .config import BOT_TOKEN, REST_API_TOKENS, CODE_RUN_API, MAIN_API
import requests
import datetime


async def start(update, context):
    user = update.effective_user

    # Перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый проект)
    list_of_states[user.id] = 'without_condition'
    the_naughty_list[user.id] = ''
    context.user_data['current_code'] = ''

    # Получение аватарки пользователя
    result = await context.bot.get_user_profile_photos(user.id)
    file_id = result['photos'][0][0]['file_id']
    file = await context.bot.get_file(file_id)
    url = file.file_path
    response = requests.get(url)
    encoded_content = base64.b64encode(response.content)

    # Создание аккаунта для юзера
    requests.post(f'{MAIN_API}/api/v1/users', json={'id': user.id, 'username': user.first_name,
                                                         'auth_date': str(datetime.date.today()),
                                                         'token': REST_API_TOKENS[0],
                                                         'photo_url': encoded_content.decode('utf-8')})
    await update.message.reply_html(
        f'👋 Привет, {user.mention_html()}. Я бот при сайте:'
        f'\n http://gaduka.sytes.net'
        f'\n'
        f'\n🐍Здесь вы можете как научиться писать код на Гадюке, так и запускать его'
        f'\n'
        f'\n👉 Чтобы узнать больше, введите /help!')


async def help_command(update, context):
    user = update.effective_user

    # Перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый проект)
    list_of_states[user.id] = 'without_condition'
    the_naughty_list[user.id] = ''
    context.user_data['current_code'] = ''

    # Создание текста для ответа
    text_message = f'🐍 Я могу помочь вам узнать больше о языке программирования Гадюка.' \
                   f' Вы можете пройти курс или почитать документацию по Гадюке,' \
                   f' а также запускать свой код на этом языке прямо здесь.' \
                   f'\n' \
                   f'\n🕹️ Вы можете использовать следующие команды:' \
                   f'\n' \
                   f'\n🗺️ Навигация:' \
                   f'\n • /help - Основная информация обо мне ' \
                   f'\n • /menu - Меню главной навигации.' \
                   f'\n' \
                   f'\n📚 Информация о гадюке:' \
                   f'\n • Сайт гадюки: https://gaduka.sytes.net/' \
                   f'\n • Документация: https://gaduka-docs.readthedocs.io/' \
                   f'\n' \
                   f'\n⌨️ Работа с языком:' \
                   f'\n • /profile - Ваши существующие проекты' \
                   f'\n • /create - Создание нового проекта' \
                   f'\n • /run - Быстрый запуск вашего кода '

    # Ответ на /help в зависимости от того была нажата кнопка или произошел вызов по команде
    try:
        await update.callback_query.message.reply_text(text_message)
    except AttributeError:
        await update.message.reply_text(text_message)


async def menu_command(update, context):
    user = update.effective_user
    message = update.effective_message

    # перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый)
    list_of_states[user.id] = 'without_condition'
    the_naughty_list[user.id] = ''
    context.user_data['current_code'] = ''

    # Создание клавиатуры
    keyboard = [
        [InlineKeyboardButton("📂 Создать новый проект", callback_data="create")],
        [InlineKeyboardButton("🚀Быстрый запуск кода", callback_data="run")],
        [InlineKeyboardButton("📚Ваш профиль и ваши проекты", callback_data="profile")],
        [InlineKeyboardButton("‍🎓Документация", url="https://gaduka-docs.readthedocs.io")],
        [InlineKeyboardButton("‍❓ Помощь", callback_data="help"),
         InlineKeyboardButton("❗️ О приложении", callback_data="about_us")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Ответ на команду /menu
    await message.reply_text(f'👋 Привет! Это главное меню нашего бота.'
                             f' Ниже вы можете найти доступные варианты действий:'
                             f'\n'
                             f'\n'
                             f'\n❕В процессе использования бота вы также можете использовать'
                             f'\n- /help'
                             f'\n- ❓ Помощь'
                             f'\nЧтобы найти справочную'
                             f' информацию для каждой команды.'
                             f'\n'
                             f'\n', reply_markup=reply_markup)


async def profile_command(update, context):
    user = update.effective_user
    # Перевод состояния юзера в подготовку к работе с конкретным проектом
    list_of_states[user.id] = 'Transition_to_editing'
    the_naughty_list[user.id] = ''
    context.user_data['current_code'] = ''

    # Получение списка проектов пользователя
    response = requests.get(f'{MAIN_API}/api/v1/users/{user.id}').json()
    result_list = response["user"]["projects"]

    # Получение аватарки пользователя
    result_photo = await context.bot.get_user_profile_photos(user.id)
    file_id = result_photo['photos'][0][0]['file_id']

    # Прохождение циклом по списку проектов пользователя и создание кнопок с их названиями
    keyboard = []
    for i in range(len(result_list)):
        keyboard_line = [InlineKeyboardButton(result_list[i]["name"],
                                              callback_data=f'run_project {result_list[i]["id"]}'
                                                            f' {result_list[i]["name"]}')]
        keyboard.append(keyboard_line)
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Текст для команды /profile
    text_message = f'❕Быстрый доступ главной навигации /help, /menu' \
                   f'\n' \
                   f'\n👨‍💻 Информация о вашем профиле:' \
                   f'\n' \
                   f'\n🆔 Id пользователя: {user.id}' \
                   f'\n' \
                   f'\n👤 Имя пользователя: {user.first_name}' \
                   f'\n' \
                   f'\n📕 Количество проектов: {len(result_list)}' \
                   f'\n' \
                   f'\n📚 Ваши проекты:'

    # Ответ на /profile в зависимости от того была нажата кнопка или произошел вызов по команде
    try:
        await update.callback_query.message.reply_photo(file_id, caption=text_message, reply_markup=reply_markup)
    except AttributeError:
        await update.message.reply_photo(file_id, caption=text_message, reply_markup=reply_markup)


async def create_command(update, context):
    user = update.effective_user

    # перевод состояния юзера в состояние создания проекта
    list_of_states[user.id] = 'creating_a_project'
    the_naughty_list[user.id] = ''
    context.user_data['current_code'] = ''

    # Создание текста для ответа
    text_message = f'👷‍♂️ Добро пожаловать в меню создания проектов!' \
                   f'\n' \
                   f'\n🙂 Вы можете создать новый проект, отправив одно любое изображение с подписью одним сообщением.' \
                   f'\n❕ Если вы не хотите отправлять изображение, просто укажите желаемое название проекта, и иконка' \
                   f' будет подобрана автоматически.' \
                   f'\n' \
                   f'\n' \
                   f'\n🌃 Отправленное фото станет иконкой проекта.' \
                   f'\n❕ Иконка проекта нужна для отображения' \
                   f' проекта на сайте.' \
                   f'\n❕ Подпись изображения станет названием проекта.' \
                   f'\n' \
                   f'\n❗️ Чтобы отменить создание проекта, используйте команду /menu или /help.'

    # Ответ на /create в зависимости от того была нажата кнопка или произошел вызов по команде
    try:
        await update.callback_query.message.reply_text(text_message)
    except AttributeError:
        await update.message.reply_text(text_message)


async def create_saving_command(update, context):
    user = update.effective_user

    # Получение данных пользователя для отправки на сервер
    source = requests.get(f'{MAIN_API}/api/v1/projects/{update.callback_query.data.split()[1]}').json()
    print(requests.put(f'{MAIN_API}/api/v1/projects/{update.callback_query.data.split()[1]}',
                       json={'code': context.user_data['current_code'],
                             'token': REST_API_TOKENS[0],
                             'name': source['project']['name'],
                             'img': source['project']['img']}).json())

    # Перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый)
    list_of_states[user.id] = 'without_condition'
    the_naughty_list[user.id] = ''
    context.user_data['current_code'] = ''

    # Оповещение пользователя об успешном сохранении
    await update.callback_query.message.reply_text('✅ Ваш проект успешно сохранен!'
                                                   '\n'
                                                   '\n❕ Вы можете просмотреть ваш проект,'
                                                   ' перейдя в меню и выбрав вкладку:'
                                                   '\n📚 Ваши существующие проекты'
                                                   '\nИли же вы можете воспользоваться'
                                                   ' командой /profile.'
                                                   '\n'
                                                   '\n🫶 Приятного кодинга! 🫶')


async def run_command(update, context):
    user = update.effective_user

    # Создание кода
    current_code = "`Место для вашего кода`"

    # Проверка открыт ли проект или же это свободный запуск
    if list_of_states[user.id] == 'Transition_to_editing':

        # Получение информации о проекте
        response = requests.get(f"{MAIN_API}/api/v1/projects/{update.callback_query.data.split()[1]}").json()

        # Создание состояния редактирования проекта
        list_of_states[user.id] = f'filling_out_the_project {update.callback_query.data.split()[1]}'
        the_naughty_list[user.id] = ''

        # Если в проекте есть код
        if response['project']['code']:

            # Сохранение кода для дальнейшей обработки
            current_code = response['project']['code']

            # Создание кнопок
            keyboard = [
                [InlineKeyboardButton("✅ Запустить код", callback_data="code_running")],
                [InlineKeyboardButton("❗️Удалить проект",
                                      callback_data=f"deletion {update.callback_query.data.split()[1]}")]]
        else:
            # Создание кнопок
            keyboard = [[InlineKeyboardButton("❗️Удалить проект",
                                              callback_data=f"deletion {update.callback_query.data.split()[1]}")]]

    else:
        # Создание состояния редактирования быстрого запуска кода
        list_of_states[user.id] = 'filling_in_an_uncreated_project'

        # Создание кнопок
        keyboard = [
            [InlineKeyboardButton("📥 Создать новый проект с текущим кодом", callback_data="create")]
        ]

    # Прикрепление кнопок
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data['current_code'] = current_code

    # Создание текста
    text_message = \
        '❓Код будет считываться ‼️полностью‼️ со следующего сообщения' \
        '\n❔Для того чтобы выйти из редактирования проекта, воспользуйтесь командой /menu. 🚪' \
        '\n' \
        '\n✏️Ваш код для быстрого запуска:' \
        '\n' \
        f'\n{current_code}' \
        '\n' \
        '\n.............................' \
        '\n' \
        '\n' \
        '\n❗️Код выводит:' \
        '\n❕Выведенный текст без фото или новое сообщение с фото следующим сообщением.' \
        '\n❕Если сообщения нет, то код ничего не выводит.' \
        '\n❕Если в процессе работы кода произойдет ошибка, то в следующем сообщении она будет выведена.'
    try:
        await update.callback_query.message.reply_text(text_message, reply_markup=reply_markup)
    except AttributeError:
        await update.message.reply_text(text_message, reply_markup=reply_markup)


async def deletion_command(update, context):
    user = update.effective_user

    requests.delete(f'{MAIN_API}/api/v1/projects/{update.callback_query.data.split()[1]}',
                    json={'token': REST_API_TOKENS[0]}).json()

    # Перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый проект)
    list_of_states[user.id] = 'without_condition'
    the_naughty_list[user.id] = ''
    context.user_data['current_code'] = ''

    # Оповещение об удалении
    await update.callback_query.message.reply_text('✅ Внимание! Ваш проект был успешно удален!'
                                                   '\n'
                                                   '\n👉 Чтобы создать новый проект, воспользуйтесь командой /create.'
                                                   '\n'
                                                   '\n🫶 Приятного кодинга! 🫶')


async def code_run_command(update, context):
    user = update.effective_user

    keyboard = [
        [InlineKeyboardButton("📂 Запустить без изображений", callback_data="launch_without_photos")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый проект)
    list_of_states[user.id] = 'the_code_is_up_and_running'
    the_naughty_list[user.id] = ''
    # Оповещение о состоянии запуска кода
    await update.callback_query.message.reply_text('🚀 Запущен код вашего проекта!'
                                                   '\n'
                                                   '\n✅ Ваш код успешно запущен,'
                                                   ' и он готов начать обработку'
                                                   ' ваших изображений.'
                                                   '\nПросто отправляйте'
                                                   ' мне изображения, и они будут обрабатываться в соответствии'
                                                   ' с вашим кодом.'
                                                   '\n'
                                                   '\n❕ Помните, что ваш код может обрабатывать только изображения,'
                                                   ' и все другие типы сообщений будут игнорироваться.'
                                                   '\n'
                                                   '\n⏰ Обработка изображений может занять некоторое время.'
                                                   ' Пожалуйста, будьте терпеливы и дождитесь завершения'
                                                   ' процесса обработки.'
                                                   '\n'
                                                   '\n👉 Если у вас есть какие-либо вопросы относительно работы кода,'
                                                   ' обратитесь к нашей команде поддержки.'
                                                   '\n'
                                                   '\n❕Для завершения работы кода воспльзуйтесь'
                                                   ' командой /help или /menu'
                                                   '\n🫶 Приятного кодинга! 🫶', reply_markup=reply_markup)


async def text_echo(update, context):
    user = update.effective_user
    message = update.effective_message
    chat_id = update.message.chat_id

    try:
        # Ответ в случае когда пользователь ничего не делает
        if list_of_states[user.id] == 'without_condition':
            await update.effective_message.reply_text('🤖 Я не понимаю, что вы написали, потому что я всего лишь бот.'
                                                      ' Однако, я могу помочь вам с выполнением определенных команд.'
                                                      '\n'
                                                      '\n❓ Чтобы получить список моих возможностей,'
                                                      ' введите команду /help.'
                                                      '\n❕Там вы найдете все необходимые инструкции и руководства'
                                                      ' по использованию меня.'
                                                      '\n'
                                                      '\n🫶 Приятного кодинга! 🫶')
        # Ответ при состоянии создания проекта
        elif list_of_states[user.id] == 'creating_a_project':
            # Проверка входит ли фотография
            if message.photo and message.media_group_id:
                # Без этого if бот отправит сообщение столько раз сколько раз сколько отправлено было фото
                # Проверка на то что фото принадлежат к разным альбомам
                if the_naughty_list[user.id] == message.media_group_id:
                    pass
                else:
                    # Ответ в случае отправки альбома вместо одного фото
                    the_naughty_list[user.id] = message.media_group_id
                    await update.effective_message.reply_text('🤖 Прости, но я не могу создать проект'
                                                              ' с несколькими иконками. '
                                                              '\n'
                                                              '\n💛 Просто отправь мне одно изображение'
                                                              ' с подписью, для того чтобы я смог создать'
                                                              ' для тебя проект'
                                                              '\n'
                                                              '\n👍 Я верю, что у тебя это получится и '
                                                              '\n🫶 Приятного кодинга! 🫶')
            else:
                # Проверка на наличие фото
                if message.photo:
                    # Проверка на наличие подписи к фото
                    if message.caption:
                        # перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый)
                        list_of_states[user.id] = 'without_condition'
                        the_naughty_list[user.id] = ''
                        context.user_data['current_code'] = ''

                        # Получение фото от пользователя и перевод его в формат base64
                        photo = update.message.photo[-1]
                        file = await context.bot.get_file(photo.file_id)
                        url = file.file_path
                        response = requests.get(url)
                        encoded_content = base64.b64encode(response.content)

                        # Проверка был ли в создаваемом проекте код
                        if context.user_data['current_code']:
                            requests.post(f'{MAIN_API}/api/v1/projects',
                                          json={'user_id': user.id,
                                                'name': message.caption,
                                                'token': REST_API_TOKENS[0],
                                                'img': encoded_content.decode('utf-8'),
                                                'code': context.user_data['current_code']})

                            # Обнуление кода
                            context.user_data['current_code'] = ''
                        else:
                            requests.post(f'{MAIN_API}/api/v1/projects',
                                          json={'user_id': user.id,
                                                'name': message.caption,
                                                'token': REST_API_TOKENS[0],
                                                'img': encoded_content.decode('utf-8')})

                        # Сообщение об успешном создании нового проекта
                        await update.effective_message.reply_text('✅ Ваш проект успешно создан!'
                                                                  '\n'
                                                                  '\n❕ Вы можете просмотреть ваш проект,'
                                                                  ' перейдя в меню и выбрав вкладку:'
                                                                  '\n📚 Ваши существующие проекты'
                                                                  '\nИли же вы можете воспользоваться'
                                                                  ' командой /profile.'
                                                                  '\n'
                                                                  '\n🫶 Приятного кодинга! 🫶')
                    else:
                        # Ответ в случае если нет подписи к фото
                        await update.effective_message.reply_text('🤖 Извините, но название'
                                                                  ' проекта обязательно для создания нового проекта.'
                                                                  '\n'
                                                                  '\n💛 Пожалуйста, отправьте мне одно изображение'
                                                                  ' с подписью, чтобы я мог создать для'
                                                                  ' вас новый проект.'
                                                                  '\n'
                                                                  '\n👍 Я верю, что у вас это получится и '
                                                                  '\n🫶 Приятного кодинга! 🫶')
                elif message.text:
                    # перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый)
                    list_of_states[user.id] = 'without_condition'
                    the_naughty_list[user.id] = ''
                    context.user_data['current_code'] = ''

                    # Обработка сообщения без фото
                    if context.user_data['current_code']:
                        # Сохранение в случае если в проекте есть код
                        requests.post(f'{MAIN_API}/api/v1/projects',
                                      json={'user_id': user.id,
                                            'name': message.text,
                                            'token': REST_API_TOKENS[0],
                                            'code': context.user_data['current_code']})
                        # Обнуление кода
                        context.user_data['current_code'] = ''
                    else:
                        # Если кода нет
                        requests.post(f'{MAIN_API}/api/v1/projects',
                                      json={'user_id': user.id,
                                            'name': message.text,
                                            'token': REST_API_TOKENS[0]})

                    # Сообщение об успешном создании нового проекта
                    await update.effective_message.reply_text('✅ Ваш проект успешно создан!'
                                                              '\n'
                                                              '\n❕ Вы можете просмотреть ваш проект,'
                                                              ' перейдя в меню и выбрав вкладку:'
                                                              '\n📚 Ваши существующие проекты'
                                                              '\nИли же вы можете воспользоваться'
                                                              ' командой /profile.'
                                                              '\n'
                                                              '\n🫶 Приятного кодинга! 🫶')
        # Ответ при состоянии редактирования проекта
        elif list_of_states[user.id].startswith('filling_out_the_project') \
                or list_of_states[user.id].startswith('filling_in_an_uncreated_project'):
            # Проверка на то что пользователь отправил текст, а не фото
            if message.text:
                # Замена текущего кода на новый
                current_code = message.text
                context.user_data['current_code'] = current_code

                if list_of_states[user.id].startswith('filling_out_the_project'):
                    # Кнопки в случае если проект уже существует
                    keyboard = [
                        [InlineKeyboardButton("📥 Сохранить код",
                                              callback_data=f"create_saving {list_of_states[user.id].split()[1]}")],
                        [InlineKeyboardButton("✅ Запустить код",
                                              callback_data="code_running")],
                        [InlineKeyboardButton("❗️Удалить проект",
                                              callback_data=f"deletion {list_of_states[user.id].split()[1]}")]
                    ]
                else:
                    # Кнопки в случае если проект еще не создан
                    keyboard = [
                        [InlineKeyboardButton("📥 Создать новый проект с текущим кодом",
                                              callback_data="create")],
                        [InlineKeyboardButton("✅ Запустить код", callback_data="code_running")]
                    ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                text_message = \
                    '❓Код будет считываться ‼️полностью‼️ со следующего сообщения' \
                    '\n❔Для того чтобы выйти из редактирования проекта, воспользуйтесь командой /menu. 🚪' \
                    '\n' \
                    '\n✏️Ваш код для быстрого запуска:' \
                    '\n' \
                    f'\n{current_code}' \
                    '\n' \
                    '\n.............................' \
                    '\n' \
                    '\n' \
                    '\n❗️Код может выводить:' \
                    '\n❕Выведенный текст без фото или новое сообщение с фото следующим сообщением.' \
                    '\n❕Если сообщения нет, то код ничего не выводит.' \
                    '\n❕Если в процессе работы кода произойдет ошибка, то в следующем сообщении она будет выведена.'
                await update.message.reply_text(text_message, reply_markup=reply_markup)

            else:
                await update.effective_message.reply_text('🤖 Прости, но похоже, ты отправил что-то не то.'
                                                          '\n'
                                                          '\n💛 Просто отправь мне текстовое сообщение без изображений,'
                                                          ' для того чтобы я смог редактировать для тебя твой код 💛'
                                                          '\n'
                                                          '\n👍 Я верю, что у тебя это получится и'
                                                          '\n🫶 Приятного кодинга! 🫶')
        # Ответ при состоянии запущенного кода
        elif list_of_states[user.id] == 'the_code_is_up_and_running':
            if message.photo:
                photo = update.message.photo[-1]
                file = await context.bot.get_file(photo.file_id)
                url = file.file_path
                response = requests.get(url)
                encoded_content = base64.b64encode(response.content)
                response = requests.post(f'{CODE_RUN_API}/api/v1/engine',
                                         json={"code": context.user_data['current_code'],
                                               "images":
                                                   ['data:image/png;base64,' + encoded_content.decode('utf-8')]}).json()
                if response["result_imgs"]:
                    image_data = base64.b64decode(response["result_imgs"][0])

                    # сохраняем файл на диск
                    with open('image.jpg', 'wb') as f:
                        f.write(image_data)

                    # отправляем изображение пользователю
                    with open('image.jpg', 'rb') as f:

                        await context.bot.send_photo(chat_id=chat_id, photo=InputFile(f),
                                                     caption=f'Итог работы вашего кода'
                                                             f':\n{response["result_text"]}')

                else:
                    await update.effective_message.reply_text(f'Итог работы вашего кода:\n{response["result_text"]}')
            else:
                pass

    except KeyError:
        # Ответ в случае когда еще не указано состояние
        await update.effective_message.reply_text('🤖 Я не понимаю, что вы написали, потому что я всего лишь бот.'
                                                  ' Однако, я могу помочь вам с выполнением определенных команд.'
                                                  '\n'
                                                  '\n❓ Чтобы получить список моих возможностей, введите команду /help.'
                                                  '\n❕Там вы найдете все необходимые инструкции и руководства'
                                                  ' по использованию меня.'
                                                  '\n'
                                                  '\n🫶 Приятного кодинга! 🫶')


async def launch_without_photos(update, context):
    response = requests.post(f'{CODE_RUN_API}/api/v1/engine',
                             json={"code": context.user_data['current_code'],
                                   "images": []}).json()
    await update.effective_message.reply_text(f'Итог работы вашего кода:\n{response["result_text"]}')


async def about_us_command(update, context):
    await update.callback_query.message.reply_text("👋Добро пожаловать в @GadukaCodeBot - ваш компаньон"
                                                   " по кодингу на языке Гадюка! 😊💻👨‍💻"
                                                   "\n"
                                                   "\n@GadukaCodeBot - это бот, который помогает"
                                                   " владеть языком программирования Гадюка,"
                                                   " начиная от простого синтаксиса и до создания сложных проектов. 🚀🌟"
                                                   "\n"
                                                   "\nОдним из основных преимуществ"
                                                   " бота является возможность запуска кода напрямую💬💻"
                                                   "\n"
                                                   "\nНо это еще не все! Гадюка предлагает создание публичных"
                                                   " проектов 🙊, в которых вы можете сохранять свой код в"
                                                   " удобной форме и в дальнейшем работать над ним."
                                                   "\n"
                                                   "\nСинтаксис языка Гадюка легок, но если у вас есть "
                                                   "вопросы, документация всегда готова ответить на них. 🤔❓"
                                                   "\n"
                                                   "\nА если вы новичок в области программирования, "
                                                   "не волнуйтесь! @GadukaCodeBot имеет возможность обучения "
                                                   "языку Гадюка прямо в боте. Вы можете получить справочную "
                                                   "информацию и практиковаться, начиная с основ и до более "
                                                   "сложных задач. 📚👨‍🎓💡"
                                                   "\n"
                                                   "\nС @GadukaCodeBot ваш опыт кодинга на Гадюке "
                                                   "будет простым и удобным. Добро пожаловать в наш "
                                                   "бот и начните свое приключение в мире маленьких змей! 🤗🤖🐍")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CallbackQueryHandler(create_command, pattern="^" + "create" + "$"))
    application.add_handler(CallbackQueryHandler(profile_command, pattern="^" + "profile" + "$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^" + "help" + "$"))
    application.add_handler(CallbackQueryHandler(about_us_command, pattern="^" + "about_us" + "$"))
    application.add_handler(CallbackQueryHandler(run_command, pattern="^" + "run" + "$"))
    application.add_handler(CallbackQueryHandler(launch_without_photos, pattern="^" + "launch_without_photos" + "$"))
    application.add_handler(CallbackQueryHandler(code_run_command, pattern="code_running"))
    application.add_handler(CallbackQueryHandler(deletion_command, pattern="deletion"))
    application.add_handler(CallbackQueryHandler(run_command, pattern="run_project"))
    application.add_handler(CallbackQueryHandler(create_saving_command, pattern="create_saving"))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run", run_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("create", create_command))
    application.add_handler(MessageHandler(filters.ALL, text_echo))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


# Словарь состояний конкретного пользователя
list_of_states = {}
# Словарь для определения того нарушил ли пользователь какое либо правило
the_naughty_list = {}


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
