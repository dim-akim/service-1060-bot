import functools
import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler
from settings import BOT_TOKEN, ADMIN_IDS
from log import get_logger
from gsheets_connector import Printers

logger = get_logger(__name__)  # Создаем логгер для обработки событий. Сообщения DEBUG - только в консоль
printers = Printers()  # Экземпляр класса Printers, в котором держатся страницы Реестра принтеров

FLOOR, ROOM, DEVICE, DATE, DONE = range(5)  # Состояния для ConversationHandler


def run_service_bot() -> None:
    """
    Запускает бота help_admin_1060_bot
    В боте реализовано ограничение на использование некоторых команд только для администраторов
    chat_id администраторов можно задать в файле settings
    """
    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher

    help_handler = CommandHandler('help', do_help)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('cartridge', cartridge_action)],
        states={
            FLOOR: [MessageHandler(Filters.text, choose_floor)],  # TODO нужен фильтр на 5-4-3-2-1 и на Привоз
            ROOM: [MessageHandler(Filters.text, choose_room)],
            DEVICE: [MessageHandler(Filters.text, choose_device)],
            DATE: [MessageHandler(Filters.text, choose_date)],
            DONE: [MessageHandler(Filters.text, cartridge_done)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    message_handler = MessageHandler(Filters.all, do_echo)

    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(message_handler)

    updater.start_polling()
    logger.info('help_admin_1060_bot успешно запустился')
    updater.idle()


def admin_access(command):
    """
    Декоратор, который ограничивает доступ к команде только для chat_id, которые перечислены в ADMIN_IDS
    """
    @functools.wraps(command)
    def wrapper(*args, **kwargs):
        update = args[0]

        if update and hasattr(update, 'message'):
            chat_id = update.message.chat_id
            if chat_id in ADMIN_IDS:
                # print(f'Доступ разрешен для {chat_id=}')
                return command(*args, **kwargs)
            else:
                logger.warning(f'Доступ запрещен для {chat_id=}')
        else:
            logger.error('Нет атрибута update.message')

    return wrapper


def start(update: Update, context: CallbackContext) -> None:
    pass


def do_echo(update: Update, context: CallbackContext) -> None:
    """
    Отправляет в чат эхо: Не знаю, что это, наберите /help
    """
    # chat_id = update.message.chat_id
    # text = update.message.text

    update.message.reply_text(  # аналог context.bot.send_message
        text='Моя твоя понимай нету\n'
             'Набери /help, чтобы узнать, что я могу'
    )


def do_help(update: Update, context: CallbackContext) -> None:
    """

    :param update:
    :param context:
    :return: None
    """
    chat_id = update.message.chat_id
    logger.info(f'{chat_id=} обратился за помощью')

    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    text = [
        f'Привет, {first_name} {last_name}',
        'Я пока не могу тебе ничего подсказать, сорян!'
    ]
    reply_text = '\n'.join(text)
    update.message.reply_text(text=reply_text)


def cartridge_action(update: Update, context: CallbackContext) -> int:
    buttons = ['Замена', 'Привоз']
    reply_markup = ReplyKeyboardMarkup.from_column(
        buttons,
        resize_keyboard=True,
    )
    update.message.reply_text('Что делаем с картриджами?', reply_markup=reply_markup)

    return FLOOR


def choose_floor(update: Update, context: CallbackContext) -> int:
    buttons = ['5', '4', '3', '2', '1']
    reply_markup = ReplyKeyboardMarkup.from_column(
        buttons,
        resize_keyboard=True,
    )
    update.message.reply_text('Выберите этаж', reply_markup=reply_markup)

    return ROOM


def choose_room(update: Update, context: CallbackContext) -> int:
    floor_number = update.message.text
    buttons = [room for room in printers.registry if room[0] == floor_number]

    reply_markup = ReplyKeyboardMarkup.from_column(
        buttons,
        resize_keyboard=True,
    )
    update.message.reply_text('Выберите кабинет', reply_markup=reply_markup)

    return DEVICE


def choose_device(update: Update, context: CallbackContext) -> int:
    room_number = update.message.text
    # TODO продумать структуру хренения элементов диалога
    context.user_data['room'] = room_number
    # TODO нужен рефакторинг
    if len(printers.registry[room_number]) == 1:
        printer_name = [key for key in printers.registry[room_number]][0]
        update.message.reply_text(f'Замена картриджа в принтере {printer_name}', reply_markup=ReplyKeyboardRemove())
        context.user_data['printer'] = printer_name
        choose_date(update, context)
        return DONE
    else:
        buttons = [printer for printer in printers.registry[room_number]]
        reply_markup = ReplyKeyboardMarkup.from_row(
            buttons,
            resize_keyboard=True,
        )
        context.user_data['printer'] = 1  # сигнал, что сюда надо записать название принтера в choose_date
        update.message.reply_text('Выберите принтер', reply_markup=reply_markup)

    return DATE


def choose_date(update: Update, context: CallbackContext) -> int:
    if context.user_data['printer'] == 1:
        context.user_data['printer'] = update.message.text
    date_format = '%d.%m.%Y'
    day = datetime.timedelta(days=1)
    today = datetime.date.today()
    yesterday = today - day

    buttons = [today.strftime(date_format), yesterday.strftime(date_format)]
    reply_markup = ReplyKeyboardMarkup.from_column(
        buttons,
        resize_keyboard=True,
    )
    update.message.reply_text(
        'Выберите день или введите дату в формате ДД.ММ.ГГГГ', reply_markup=reply_markup
    )

    return DONE


def cartridge_done(update: Update, context: CallbackContext) -> int:
    # TODO реализовать занесение в таблицу и правильную запись в лог
    room = context.user_data['room']
    printer = context.user_data['printer']
    date = update.message.text
    username = update.message.from_user.username

    logger.info(f'Замена: {username=} {room=} {printer=} {date=}')

    message = f'Замена картриджа\nКабинет: {room}\nПринтер: {printer}\nДата: {date}'
    update.message.reply_text(
        message, reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat_id
    logger.info(f'{chat_id=} {user.first_name} отменил команду')  # TODO вытащить предыдущую команду
    update.message.reply_text(
        'Ничего не делаем. Отмена', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


if __name__ == '__main__':
    run_service_bot()
