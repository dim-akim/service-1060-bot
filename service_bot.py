import functools
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler
from settings import BOT_TOKEN, ADMIN_IDS
from log import get_logger
from gsheets_connector import Printers

logger = get_logger(__name__)  # Создаем логгер для обработки событий. Сообщения DEBUG - только в консоль
printers = Printers()  # Экземпляр класса Printers, в котором держатся страницы Реестра принтеров

ROOM, DEVICE = range(2)  # Состояния для ConversationHandler


def run_service_bot() -> None:
    """
    Запускает бота help_admin_1060_bot
    В боте реализовано ограничение на использование некоторых команд только для администраторов
    chat_id администраторов можно задать в файле settings
    """
    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher

    help_handler = CommandHandler('help', do_help)
    keyboard_handler = CommandHandler('keyboard', answer_with_keyboard)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('change_cartridge', trigger_cartridge_change)],
        states={
            ROOM: [MessageHandler(Filters.text, choose_room)],
            DEVICE: [MessageHandler(Filters.text, choose_device)]
        },
        fallbacks=[]
    )
    message_handler = MessageHandler(Filters.all, do_echo)

    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(keyboard_handler)
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


def answer_with_keyboard(update: Update, context: CallbackContext) -> None:
    # Для клавиатуры нужна матрица (двумерный список) из текстовых элементов
    # Каждый текстовый элемент - отдельная кнопка

    button_list = [
        [
            'col1',
            'col2',
            'col3'
        ],
        [
            'row2 col1',
            'row2 col2'
        ]
    ]

    # Теперь собираем кнопки в клавиатуру - объект ReplyKeyboardMarkup
    # Для одной кнопки в строке можно использовать одномерный список и метод from_column
    reply_markup = ReplyKeyboardMarkup(
        button_list,  # список кнопок
        resize_keyboard=True,  # сжимает кнопки по вертикали до высоты текста
        one_time_keyboard=True  # убирает клавиатуру после нажатия на кнопку
    )
    update.message.reply_text("A three-column menu", reply_markup=reply_markup)


def trigger_cartridge_change(update: Update, context: CallbackContext) -> int:
    keyboard = ['5', '4', '3', '2', '1']
    reply_markup = ReplyKeyboardMarkup.from_column(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    update.message.reply_text('Выберите этаж', reply_markup=reply_markup)

    return ROOM


def choose_room(update: Update, context: CallbackContext) -> int:
    floor_number = update.message.text
    rooms = [room for room in printers.registry if room[0] == floor_number]

    reply_markup = ReplyKeyboardMarkup.from_column(
        rooms,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    update.message.reply_text('Выберите кабинет', reply_markup=reply_markup)
    return DEVICE


def choose_device(update: Update, context: CallbackContext) -> int:
    room_number = update.message.text
    if len(printers.registry[room_number]) == 1:
        update.message.reply_text(f'Замена картриджа в принтере {printers.registry[room_number]}')
    else:
        keyboard = [printer for printer in printers.registry[room_number]]
        reply_markup = ReplyKeyboardMarkup.from_row(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        update.message.reply_text('Выберите принтер', reply_markup=reply_markup)
    return ConversationHandler.END


if __name__ == '__main__':
    run_service_bot()
