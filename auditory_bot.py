import functools
import datetime
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from settings import ECHO_TOKEN
from log import get_logger


logger = get_logger(__name__)  # TODO переделать file_handler


def log_action(command):
    """
    Декоратор, который логирует все действия бота и возникающие ошибки
    """

    @functools.wraps(command)
    def wrapper(*args, **kwargs):
        try:
            update = args[0]
            username = update.message.from_user.username
            logger.info(f'{username} вызвал функцию {command.__name__}')
            return command(*args, **kwargs)
        except:
            logger.exception(f'Ошибка в обработчике {command.__name__}')
            raise

    return wrapper


def main():
    updater = Updater(token=ECHO_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('takekey', take_key))
    dispatcher.add_handler(CommandHandler('passkey', pass_key))
    dispatcher.add_handler(CommandHandler('wherekey', where_key))
    dispatcher.add_handler(CommandHandler('gethistory', get_history))

    dispatcher.add_handler(MessageHandler(Filters.all, do_help))

    updater.start_polling()
    logger.info('auditory_bot успешно запустился')
    updater.idle()


def take_key(update: Update, context: CallbackContext):
    user = update.message.from_user
    if 'key_taken' not in context.chat_data:
        context.chat_data['key_taken'] = False
    if context.chat_data['key_taken']:
        reply = f'Ключ передал {context.chat_data["user"]}'
        logger.debug(reply)
        update.message.reply_text(text=reply)
    context.chat_data['key_taken'] = True
    context.chat_data['user'] = f'{user.first_name} {user.last_name}'

    reply = f'Ключ взял {user.first_name} {user.last_name}'
    logger.debug(reply)
    update.message.reply_text(text=reply)


def pass_key(update: Update, context: CallbackContext):
    user = update.message.from_user
    # TODO учесть случай, когда ключа ни у кого нет
    context.chat_data['key_taken'] = False
    context.chat_data['user'] = ''

    reply = f'Ключ сдал {user.first_name} {user.last_name}'
    logger.debug(reply)
    update.message.reply_text(text=reply)


def where_key(update: Update, context: CallbackContext):
    if context.chat_data['key_taken']:
        user = update.message.from_user
        reply = f'Ключ взял {user.first_name} {user.last_name}'
        logger.debug(reply)
        update.message.reply_text(text=reply)
    else:
        reply = f'Ключ на вахте'
        logger.debug(reply)
        update.message.reply_text(text=reply)


def get_history(update: Update, context: CallbackContext):
    update.message.reply_text(text='С этим пока трудности, работаем...')


def do_help(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text(
        text=f'Привет, {user.first_name} {user.last_name}!\n\n'
             f'Вот команды, которые я понимаю:\n'
             f'/takekey - я запишу ключ на твое имя\n'
             f'/passkey - я запишу, что ты сдал ключ на вахту\n'
             f'/wherekey - я расскажу, у кого ключ\n'
             f'/gethistory - я расскажу, кто последний брал ключ\n'
    )


if __name__ == '__main__':
    main()
