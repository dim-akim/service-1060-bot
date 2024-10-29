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
"""
import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from settings import Config
from utils.log import file_handler, console_handler
import handlers.admin as admin_handlers


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s - %(message)s (%(filename)s:%(lineno)d)",
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)


def run_1060_bot():
    """Запускает бота @help_admin_1060_bot
    """
    app = ApplicationBuilder().token(Config.bot_token).build()

    app.add_handler(CommandHandler(["start", "help"], do_help))
    admin_handlers.register(app)

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
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name

    logger.info(f'{chat_id=} {first_name} {last_name} обратился за помощью')
    reply_lines = [
        f'Привет, {first_name} {last_name}',
        'Я умею реагировать на следующие команды:',
        '/cartridge - начать диалог по замене картриджей (поступление пока в разработке)',
        '/cancel - закончить диалог на этом этапе',
        '/help - мануал, который ты сейчас читаешь.',
    ]
    await update.message.reply_text(
        text='\n'.join(reply_lines),
        reply_markup=ReplyKeyboardRemove()
    )


if __name__ == '__main__':
    run_1060_bot()
