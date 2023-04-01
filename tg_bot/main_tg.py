import base64
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN, REST_API_TOKENS
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
    requests.post('http://127.0.0.1/api/v1/users', json={'id': user.id, 'username': user.first_name,
                                                         'auth_date': str(datetime.date.today()),
                                                         'token': REST_API_TOKENS[0],
                                                         'photo_url': encoded_content.decode('utf-8')})
    await update.message.reply_html(
        f'👋 Привет, {user.mention_html()}. Я бот при сайте:'
        f'\n http://gaduka.sytes.net'
        f'\n'
        f'\n🐍Здесь ты можешь как научиться писать код, так и запустить его'
        f'\n'
        f'\n👉 Чтобы узнать больше, введи /help!')


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
                   f'\n • /doc - Документация и курс по гадюке' \
                   f'\n' \
                   f'\n⌨️ Работа с языком:' \
                   f'\n • /profile - Твои существующие проекты' \
                   f'\n • /create - Создание нового проекта' \
                   f'\n • /run - Быстрый запуск кода '

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

    # Получение аватарки пользователя
    result = await context.bot.get_user_profile_photos(user.id)
    file_id = result['photos'][0][0]['file_id']

    # Создание клавиатуры
    keyboard = [
        [InlineKeyboardButton("📂 Создать новый проект", callback_data="create")],
        [InlineKeyboardButton("🚀Быстрый запуск кода", callback_data="run")],
        [InlineKeyboardButton("📚 Твои существующие проекты", callback_data="profile")],
        [InlineKeyboardButton("‍🎓Курс и документация", callback_data="dok")],
        [InlineKeyboardButton("‍❓ Помощь", callback_data="help"),
         InlineKeyboardButton("❗️ О приложении", callback_data="help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Получение информации о пользователе
    response = requests.get(f'http://127.0.0.1/api/v1/users/{user.id}')

    # Ответ на команду /menu
    await message.reply_photo(file_id, caption=f'👋 Привет! Это главное меню нашего бота.'
                                               f' Ниже вы можете найти доступные варианты действий:'
                                               f'\n'
                                               f'\n'
                                               f'\n❕В процессе использования бота вы также можете использовать команду'
                                               f'\n/help'
                                               f'\nИли нажать на кнопку '
                                               f'\n❓ Помощь'
                                               f'\nЧтобы найти справочную'
                                               f' информацию для каждой команды.'
                                               f'\n'
                                               f'\n', reply_markup=reply_markup)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CallbackQueryHandler(help_command, pattern="^" + "help" + "$"))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))

    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    # Словарь состояний конкретного пользователя
    list_of_states = {}
    # Словарь для определения того нарушил ли пользователь какое либо правило
    the_naughty_list = {}
    main()
