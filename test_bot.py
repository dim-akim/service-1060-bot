"""
Здесь можно тестировать отдельные функции из модулей:
    handlers.admin
    handlers.teacher

Тестирование ведется с помощью бота https://t.me/echo_waldorf_bot
"""
import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from settings import ECHO_TOKEN
# from utils.log import get_logger
import handlers.admin as handlers_a

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
# logger = get_logger(__name__)  # Создаем логгер для обработки событий. Сообщения DEBUG - только в консоль


def run_1060_bot():
    """Запускает бота @help_admin_1060_bot
    """
    app = ApplicationBuilder().token(ECHO_TOKEN).build()

    handlers_a.register_admin_handlers(app)
    # app.add_handler(CommandHandler("hello", handlers_a.cartridge_choose_action))
    app.add_handler(MessageHandler(filters.Text(), echo))

    app.run_polling()


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    userid = update.message.from_user.id
    text = [
        'Привет! Ты находишься в режиме тестирования.',
        'Мне известна команда /cartridge.',
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