"""
Здесь можно тестировать отдельные функции из модулей:
    handlers.admin
    handlers.teacher

Тестирование ведется с помощью бота https://t.me/echo_waldorf_bot
"""
import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP, DAY
from settings import ECHO_TOKEN
# from utils.log import get_logger
import handlers.admin as handlers_a

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
# logger = get_logger(__name__)  # Создаем логгер для обработки событий. Сообщения DEBUG - только в консоль


class MyCalendar(DetailedTelegramCalendar):
    first_step = DAY


def run_1060_bot():
    """Запускает бота @help_admin_1060_bot
    """
    app = ApplicationBuilder().token(ECHO_TOKEN).build()

    handlers_a.register_admin_handlers(app)
    # app.add_handler(CommandHandler("hello", handlers_a.cartridge_choose_action))
    app.add_handler(CommandHandler('calendar', call_calendar))
    app.add_handler(CallbackQueryHandler(MyCalendar.func()))
    app.add_handler(MessageHandler(filters.Text(), echo))

    app.run_polling()


async def call_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    calendar, step = MyCalendar(locale='ru').build()
    await update.message.reply_text(f'Выберите {LSTEP[step]}', reply_markup=calendar)


async def calendar_react(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    # await query.answer()
    result, key, step = MyCalendar(locale='ru').process(query.data)
    print(f'{result=} {key=} {step=}')
    if not result and key:
        await query.edit_message_text(f"Выберите {LSTEP[step]}", reply_markup=key)
    elif result:
        await query.edit_message_text(f"Вы выбрали {result}")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    userid = update.message.from_user.id
    text = [
        'Привет! Ты находишься в режиме тестирования.',
        'Мне известны команды:'
        '/cartridge - начать диалог по замене картриджей.'
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
