from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f'👋 Привет, {user.mention_html()}. Я бот при сайте:'
        f'\n http://gaduka.sytes.net'
        f'\n'
        f'\n🐍Здесь ты можешь как научиться писать код, так и запустить его'
        f'\n'
        f'\n👉 Чтобы узнать больше, введи /help!')


async def help_command(update, context):
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


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
