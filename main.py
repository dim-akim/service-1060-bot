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

Переход на Python версии 3.11.1 и библиотеку python-telegram-bot версии 20.0 (асинхронность)
"""
import functools
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from settings import ECHO_TOKEN, ADMIN_IDS


def run_1060_bot():
    """Запускает бота @help_admin_1060_bot
    """
    app = ApplicationBuilder().token(ECHO_TOKEN).build()

    app.add_handler(CommandHandler("hello", hello))

    app.run_polling()


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')



