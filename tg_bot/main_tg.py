import json

import telegram
import base64
from telegram import Update, Message
from io import BytesIO
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN, REST_API_TOKENS
import requests
import datetime


async def start(update, context):
    # перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый)
    user = update.effective_user
    list_of_states[user.id] = 'without condition'

    response = requests.post('http://127.0.0.1/api/v1/users',
                             json={'id': user.id, 'username': user.first_name,
                                   'auth_date': str(datetime.date.today()),
                                   'token': REST_API_TOKENS[0], 'photo_url': 'bbbbbbbbbb'})
    await update.message.reply_html(
        f'👋 Привет, {user.mention_html()}. Я бот при сайте:'
        f'\n http://gaduka.sytes.net'
        f'\n'
        f'\n🐍Здесь ты можешь как научиться писать код, так и запустить его'
        f'\n'
        f'\n👉 Чтобы узнать больше, введи /help!')


async def help_command(update, context):
    # перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый)
    user = update.effective_user
    list_of_states[user.id] = 'without condition'

    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text(
        f'🐍 Я могу помочь вам узнать больше о гадюке.'
        f' У меня вы можете пройти курс или почитать документацию по гадюке.'
        f'\nТак же вы можете запускать свой код прямо здесь.'
        f'\n'
        f'\n🕹️ Вы можете использовать следующие команды:'
        f'\n'
        f'\n🗺️ Навигация:'
        f'\n • /help - Основная информация обо мне '
        f'\n • /menu - Меню главной навигации.'
        f'\n'
        f'\n📚 Информация о гадюке:'
        f'\n • /doc - Документация '
        f'\n • /course - Курс по гадюке '
        f'\n'
        f'\n⌨️ Работа с языком:'
        f'\n • /profile - Твои существующие проекты'
        f'\n • /create - Создание нового проекта'
        f'\n • /run - Быстрый запуск кода ')


async def menu_command(update, context):
    # перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый)
    user = update.effective_user
    list_of_states[user.id] = 'without condition'
    the_naughty_list[user.id] = ''

    message = update.effective_message
    user_id = update.effective_user.id
    result = await context.bot.get_user_profile_photos(user_id)
    photos = result['photos']
    photo = photos[0][0]
    file_id = photo['file_id']
    keyboard = [
        [InlineKeyboardButton("📚Твои существующие проекты", callback_data="profile")],
        [InlineKeyboardButton("📝Создание нового проекта", callback_data="create")],
        [InlineKeyboardButton("🖊Быстрый запуск кода", callback_data="run")],
        [InlineKeyboardButton("📖Документация", callback_data="run"),
         InlineKeyboardButton("‍🎓Курс по гадюке", callback_data="run")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    response = requests.get(f'http://127.0.0.1/api/v1/users/{user_id}')
    await message.reply_photo(file_id, caption=f'Id пользователя: {user_id}'
                                               f'\nКоличество проектов: '
                                               f'{len(response.json()["user"]["projects"])}',
                              reply_markup=reply_markup)


async def profile_command(update: Update, context):
    # перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый)
    user = update.effective_user
    list_of_states[user.id] = 'without condition'

    user_id = update.effective_user.id
    response = requests.get(f'http://127.0.0.1/api/v1/users/{user_id}')
    keyboard = []
    for i in range(len(response.json()["user"]["projects"])):
        keyboard_line = [InlineKeyboardButton(response.json()["user"]["projects"][i]['name'],
                                              callback_data=f'{response.json()["user"]["projects"][i]["name"]}'
                                                            f'_{response.json()["user"]["projects"][i]["id"]}')]
        keyboard.append(keyboard_line)
    reply_markup = InlineKeyboardMarkup(keyboard)

    text_message = '📖Ваши проекты:'
    try:
        await update.callback_query.message.reply_text(text_message, reply_markup=reply_markup)
    except AttributeError:
        await update.message.reply_text(text_message, reply_markup=reply_markup)


async def create_command(update, context):
    user = update.effective_user
    list_of_states[user.id] = 'creating a project'
    text_message = '🙂 Отправьте одно любое изображение с подписью одним сообщением.' \
                   '\n😕Или только желаемое название проекта. ' \
                   '\n🤖В таком случае иконка будет подобрана автоматически.' \
                   '\n' \
                   '\n🌃 Отправленное фото станет иконкой проекта.' \
                   '\nИконка проекта нужна для отображения проекта на сайте.' \
                   '\n🖊 Подпись изображения станет названием проекта.' \
                   '\n' \
                   '\n❗️Для отмены создания проекта используйте команду /menu.'

    try:
        await update.callback_query.message.reply_text(text_message)
    except AttributeError:
        await update.message.reply_text(text_message)


async def run_command(update, context):
    # перевод состояния юзера в неактивный режим(не заполняет проект, не создает новый)
    user = update.effective_user
    list_of_states[user.id] = 'filling out the project'

    current_code = ""
    keyboard = [
        [InlineKeyboardButton("📥 Создать новый проект с текущим кодом", callback_data="create")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text_message = \
        'Код будет считываться ‼️полностью‼️ со следующего сообщения' \
        '\n' \
        '\n✏️Ваш код для быстрого запуска:' \
        '\n' \
        '\n#***Место для вашего кода***' \
        f'\n{current_code}' \
        '\n.............................' \
        '\n' \
        '\n' \
        '\n❗️Код выводит:' \
        '\n❕Выведенный текст без фото или новое сообщение с фото следующим сообщением.' \
        '\n❕Если сообщения нет то код ничего не выводит.' \
        '\n❕Если в процессе работы кода произойдет ошибка то в следующем сообщении она будет выведенна.'
    try:
        await update.callback_query.message.reply_text(text_message, reply_markup=reply_markup)
    except AttributeError:
        await update.message.reply_text(text_message, reply_markup=reply_markup)


async def text_echo(update, context):
    user = update.effective_user
    if list_of_states[user.id] == 'without condition':
        await update.effective_message.reply_text('🤖Извините я не понимаю, что вы написали ведь я всего лишь бот'
                                                  '\n'
                                                  '\nПопробуйде команду 👉/help👈 для того чтобы узнать мои возможности'
                                                  '\n'
                                                  '\n🫶Удачного кодинга🫶')
    elif list_of_states[user.id] == 'creating a project':
        message = update.effective_message
        media_group_id = message.media_group_id
        if message.photo and media_group_id:
            if the_naughty_list[user.id]:
                pass
            else:
                the_naughty_list[user.id] = media_group_id
                await update.effective_message.reply_text('🤖 Прости, но я просил только одно изображение. '
                                                          '\nА когда ты присылаешь больше,'
                                                          ' то я не могу определиться, какое лучше'
                                                          ' подходит для иконки проекта 👉👈 '
                                                          '\n'
                                                          '\n💛 Просто отправь мне одно изображение'
                                                          ' с подписью, для того чтобы я смог создать'
                                                          ' для тебя новый проект 💛 '
                                                          '\n'
                                                          '\n👍 Я верю, что у тебя это получится и '
                                                          '\n🫶 Удачного кодинга! 🫶')
        else:
            the_naughty_list[user.id] = ''
            if message.photo:
                if message.caption:
                    # в разработке
                    list_of_states[user.id] = 'without condition'
                    photo = update.message.photo[-1]
                    file = await context.bot.get_file(photo.file_id)
                    url = file.file_path
                    response = requests.get(url)
                    encoded_content = base64.b64encode(response.content)
                    response = requests.post('http://127.0.0.1/api/v1/projects',
                                             json={'user_id': user.id, 'name': message.caption,
                                                   'token': REST_API_TOKENS[0], 'img': encoded_content.decode('utf-8')})
                    await update.effective_message.reply_text('✅Ваш проект создан'
                                                              '\n'
                                                              '\n❕ Вы сможете увидеть его,'
                                                              ' если в меню перейдете во вкладку'
                                                              '\n⬜️⬜️⬜️📚 Твои существующие проекты ⬜️⬜️⬜️'
                                                              '\n❕ Или если воспользуетесь командой /profile.'
                                                              '\n'
                                                              '\n🫶 Удачного кодинга! 🫶')
                else:
                    await update.effective_message.reply_text('🤖 Прости, но название проекту обязательно нужно'
                                                              '\n'
                                                              '\n💛 Просто отправь мне одно изображение'
                                                              ' с подписью, для того чтобы я смог создать'
                                                              ' для тебя новый проект 💛 '
                                                              '\n'
                                                              '\n👍 Я верю, что у тебя это получится и '
                                                              '\n🫶 Удачного кодинга! 🫶')
            elif message.text:
                response = requests.post('http://127.0.0.1/api/v1/projects',
                                         json={'user_id': user.id, 'name': message.text,
                                               'token': REST_API_TOKENS[0]})
                list_of_states[user.id] = 'without condition'
                await update.effective_message.reply_text('✅Ваш проект создан'
                                                          '\n'
                                                          '\n❕ Вы сможете увидеть его, если в меню перейдете во вкладку'
                                                          '\n  ⬜️⬜️⬜️📚 Твои существующие проекты ⬜️⬜️⬜️'
                                                          '\n❕ Или если воспользуетесь командой /profile.'
                                                          '\n'
                                                          '\n🫶 Удачного кодинга! 🫶')


def formatting_in_base64(result_imgs):
    imgs_json = []
    for img in result_imgs:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        a = base64.b64encode(buffered.getvalue()).decode("utf-8")
        imgs_json.append(json.dumps(a))
    return imgs_json


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CallbackQueryHandler(profile_command, pattern="^" + "profile" + "$"))
    application.add_handler(CallbackQueryHandler(create_command, pattern="^" + "create" + "$"))
    application.add_handler(CallbackQueryHandler(run_command, pattern="^" + "run" + "$"))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("create", create_command))
    application.add_handler(CommandHandler("run", run_command))
    application.add_handler(MessageHandler(filters.ALL, text_echo))
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    list_of_states = {}
    the_naughty_list = {}
    main()
