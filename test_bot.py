"""
Здесь можно тестировать отдельные функции из модулей:
    handlers.admin
    handlers.teacher

Тестирование ведется с помощью бота https://t.me/echo_waldorf_bot
"""
import datetime
import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from settings import Config
from utils.log import file_handler, console_handler
import handlers.admin as admin_handlers
from utils.inline_calendar import MyCalendar, RU_STEP

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s - %(message)s (%(filename)s:%(lineno)d)",
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)
# TODO вынести настройки логгера в отдельный файл


def run_1060_bot():
    """Запускает бота @help_admin_1060_bot
    """
    app = ApplicationBuilder().token(Config.echo_token).build()

    admin_handlers.register(app)
    # app.add_handler(CommandHandler("hello", handlers_a.cartridge_choose_action))
    app.add_handler(CommandHandler('calendar', call_calendar))
    app.add_handler(CallbackQueryHandler(calendar_react, MyCalendar.func()))
    app.add_handler(MessageHandler(filters.Text(), echo))

    app.run_polling()


async def call_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    calendar, step = MyCalendar(locale='Ru', max_date=datetime.date.today()).build()
    await update.message.reply_text(f'Выберите {RU_STEP[step]}', reply_markup=calendar)


async def calendar_react(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    result, key, step = MyCalendar(locale='Ru', max_date=datetime.date.today()).process(query.data)
    if not result and key:
        await query.edit_message_text(f"Выберите {RU_STEP[step]}", reply_markup=key)
    elif result:
        await query.edit_message_text(f"Вы выбрали {result=}")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    userid = update.message.from_user.id
    text = [
        'Привет! Ты находишься в режиме тестирования.',
        'Мне известны команды:',
        '/cartridge - начать диалог по замене картриджей.',
        '/calendar - тестирование календаря.',
        'Нажми и увидишь, что будет.',
        f'На всякий случай, твой {userid=}'
    ]
    text = '\n'.join(text)
    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardRemove()
    )


if __name__ == '__main__':
    run_1060_bot()
