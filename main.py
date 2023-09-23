"""
Бот для Вальдорфской школы имени А.А. Пинского
В боте реализовано ограничение на использование некоторых команд только для администраторов
chat_id администраторов можно задать в файле settings

Функционал:
    (СисАдмин) Фиксация даты замены очередного картриджа
    TODO (СисАдмин) Фиксация моделей и количества привезенных картриджей
    (СисАдмин) Создание индивидуальных таблиц с оценками для рассылки по классам
    TODO Создание и подтверждение заявки на урок или мероприятие в Актовом зале
    TODO Создание заявки на техническое обслуживание

Переход на Python версии 3.11.1 и библиотеку python-telegram-bot версии 20.1 (асинхронность)
"""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from settings import ECHO_TOKEN
from utils.log import get_logger


logger = get_logger(__name__)  # Создаем логгер для обработки событий. Сообщения DEBUG - только в консоль


def run_1060_bot():
    """Запускает бота @help_admin_1060_bot
    """
    app = ApplicationBuilder().token(ECHO_TOKEN).build()

    app.add_handler(CommandHandler("hello", hello))

    app.run_polling()


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def do_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Выводит сообщение о доступных командах.
    Команды собираются на основе функций register_<some_role>_handlers TODO доработать
    """
    # TODO переделать, продумать два уровня команд - для учителя и для админа
    chat_id = update.message.chat_id
    logger.debug(f'{chat_id=} обратился за помощью')

    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    reply_lines = [
        f'Привет, {first_name} {last_name}',
        'Я умею реагировать на следующие команды:',
        '/cartridge - начать диалог по замене картриджей (поступление пока в разработке)',
        '/cancel - закончить диалог на этом этапе',
        '/help - мануал, который ты сейчас читаешь.',
    ]
    text = '\n'.join(reply_lines)
    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardRemove()
    )
