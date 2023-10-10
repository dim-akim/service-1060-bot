import datetime

import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler
from telegram.ext import ContextTypes, Application, filters
from telegram.constants import ChatAction

# from utils.log import get_logger
from gsheets_connector import Printers
from utils import validators
from utils.keyboards import make_inline_keyboard

# logger = get_logger(__name__)  # Создаем логгер для обработки событий. Сообщения DEBUG - только в консоль
# TODO refactor - класс Printer, в котором будет информация о конкретном принтере
printers = Printers()  # Экземпляр класса Printers, в котором держатся страницы Реестра принтеров
FLOOR, ROOM, DEVICE, DATE, DONE = range(5)  # Состояния для диалога по картриджам


def register_admin_handlers(app: Application):
    """
    Добавляет боту следующие обработчики:
        cartridge_conv_handler - диалог по смене картриджа в одном из принтеров,
            перечисленных в Google-таблице "Реестр принтеров"
            https://docs.google.com/spreadsheets/d/1WeyL-_Eoj5UYAVyF6YjEbndDV8wXfg821iUA_R7C5YE/edit#gid=451124063

    :param app: экземпляр :class:`telegram.ext.Application`
    :return:
    """
    # TODO добавить диалог для привоза картриджей
    cancel_handler = CommandHandler('cancel', cancel)
    cartridge_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('cartridge', cartridge_choose_action)
        ],
        states={
            FLOOR: [
                cancel_handler,
                # ^ means "start of line/string"
                # $ means "end of line/string"
                # So ^ABC$ will only allow 'ABC'
                CallbackQueryHandler(cartridge_choose_floor, pattern='^' 'Замена' '$'),
                CallbackQueryHandler(cartridge_incoming, pattern='^' 'Привоз' '$'),
                MessageHandler(filters.Text(), cartridge_choose_floor),
            ],
            ROOM: [
                cancel_handler,
                CallbackQueryHandler(cartridge_choose_room, pattern='^' 'change_[12345]_floor' '$'),
                MessageHandler(filters.Text(), cartridge_choose_room),
            ],
            DEVICE: [
                cancel_handler,
                CallbackQueryHandler(cartridge_choose_device),  # TODO нужен паттерн
                MessageHandler(filters.Text(), cartridge_choose_device),
            ],
            DATE: [
                cancel_handler,
                CallbackQueryHandler(cartridge_choose_date),  # TODO нужен паттерн
                MessageHandler(filters.Text(), cartridge_choose_date),
            ],
            DONE: [
                cancel_handler,
                CallbackQueryHandler(cartridge_change_done),  # TODO нужен паттерн
                MessageHandler(filters.Regex(validators.DATE), cartridge_change_done),
                MessageHandler(filters.Text(), cartridge_wrong_date),
            ],
        },
        fallbacks=[cancel_handler]
    )

    app.add_handler(cartridge_conv_handler)


async def cartridge_choose_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Стартует диалог по картриджам. Есть две опции:
        Замена - зарегистрировать замену картриджа в конкретном принтере
        Привоз - записать количество привезенных картриджей

    :return: :obj:`int`: Состояние FLOOR - выбор этажа
    """
    buttons = ['Замена', 'Привоз']
    reply_markup = make_inline_keyboard(buttons)
    # TODO запомнить id сообщения, чтобы его можно было потом редактировать
    await update.message.reply_text(
        'Что делаем с картриджами?',
        reply_markup=reply_markup
    )

    return FLOOR


async def cartridge_choose_floor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Первый этап из диалога по замене картриджей: **Этаж**-Кабинет-Принтер-Дата-Готово.

    Дает пользователю выбрать этаж, на котором стоит принтер.
    Заменяет кнопки, которые были на полученном сообщении

    :return: Состояние ROOM - выбор кабинета
    """
    query = update.callback_query
    await query.answer()

    buttons = {
        '1': 'change_1_floor',
        '2': 'change_2_floor',
        '3': 'change_3_floor',
        '4': 'change_4_floor',
        '5': 'change_5_floor'
    }
    reply_markup = make_inline_keyboard(buttons)
    # TODO добавить кнопки "Назад" и "Отмена", нужна функция

    await query.edit_message_text(
        'Замена картриджа\n'
        'Выберите этаж',
        reply_markup=reply_markup
    )

    return ROOM


async def cartridge_choose_room(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Второй этап из диалога по замене картриджей: Этаж-**Кабинет**-Принтер-Дата-Готово.

    Дает пользователю выбрать кабинет, в котором стоит принтер.

    :return: Состояние DEVICE - выбор принтера
    """
    query = update.callback_query
    floor_number = query.data[7]
    buttons = [room for room in printers.registry if room[0] == floor_number]
    if len(buttons) == 0:
        await query.answer(f'На {floor_number} этаже не зарегистрировано работающих принтеров')
        # await context.bot.send_message(
        #     chat_id=update.effective_chat.id,
        #     text=f'На {floor_number} этаже не зарегистрировано работающих принтеров'
        # )
        return ROOM
    await query.answer()
    reply_markup = make_inline_keyboard(buttons)
    await query.edit_message_text(
        'Замена картриджа\n'
        'Выберите кабинет',
        reply_markup=reply_markup
    )

    return DEVICE


async def cartridge_choose_device(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Третий этап из диалога по замене картриджей: Этаж-Кабинет-**Принтер**-Дата-Готово.

    Дает пользователю выбрать принтер, если в кабинете их стоит больше одного.
    Если принтер в кабинете единственный, сразу переходит к следующему этапу диалога.

    :return: Состояние DATE - выбор даты замены
    """
    query = update.callback_query
    await query.answer()
    room_number = query.data
    context.user_data['room'] = room_number
    buttons = [printer for printer in printers.registry[room_number]]
    if len(buttons) == 1:
        context.user_data['printer'] = buttons[0]
        return await cartridge_choose_date(update, context)

    else:
        reply_markup = make_inline_keyboard(buttons)
        context.user_data['printer'] = 1  # сигнал, что сюда надо записать название принтера в choose_date
        await query.edit_message_text(
            'Замена картриджа\n'
            f'Кабинет: {room_number}\n'
            'Выберите принтер',
            reply_markup=reply_markup
        )

    return DATE


async def cartridge_choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Четвертый этап из диалога по замене картриджей: Этаж-Кабинет-Принтер-**Дата**-Готово.

    Дает пользователю выбрать дату замены картриджа.

    :return: Состояние DONE - регистрация замены в таблице
    """
    query = update.callback_query
    await query.answer()
    if context.user_data['printer'] == 1:
        context.user_data['printer'] = query.data

    # TODO вынести в отдельную функцию
    # TODO сделать календарь
    date_format = '%d.%m.%Y'
    day = datetime.timedelta(days=1)
    today = datetime.date.today()
    yesterday = today - day
    today, yesterday = [day.strftime(date_format) for day in (today, yesterday)]

    buttons = {
        f'Сегодня {today}': today,
        f'Вчера {yesterday}': yesterday,
    }
    reply_markup = make_inline_keyboard(buttons, cancel_btn=True)
    text = [
        'Замена картриджа\n'
        f'Кабинет: {context.user_data["room"]}',
        f'Принтер: {context.user_data["printer"]}',
        'Выберите день или введите дату в формате ДД.ММ.ГГГГ'
    ]
    text = '\n'.join(text)
    dialog = await query.edit_message_text(
        text,
        reply_markup=reply_markup
    )
    context.user_data['dialog'] = dialog
    return DONE


async def cartridge_wrong_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Четвертый этап из диалога по замене картриджей: Этаж-Кабинет-Принтер-**Дата**-Готово.

    Повторно запрашивает дату от пользователя в случае, если тот ее указал не по формату

    :return: Состояние DONE - регистрация замены в таблице
    """
    chat_id = update.message.chat_id
    dialog: telegram.Message = context.user_data['dialog']
    text = dialog.text
    reply_markup = dialog.reply_markup
    await update.message.delete()
    await update.message.reply_text(
        'Неверный формат даты!'
    )
    # new_dialog = await update.message.reply_text(
    #     text=text,
    #     reply_markup=reply_markup
    # )
    # context.user_data['dialog'] = new_dialog
    return DONE


async def cartridge_change_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Последний этап из диалога по замене картриджей: Этаж-Кабинет-Принтер-Дата-**Готово**.

    Регистрирует замену картриджа в Google-таблице и выдает сообщение о предыдущей замене.

    :return: Состояние ConversationHandler.END
    """
    # TODO реализовать занесение в таблицу и правильную запись в лог
    if update.callback_query:
        await update.callback_query.answer()
        date = update.callback_query.data
    else:
        date = update.message.text
    room = context.user_data['room']
    printer = context.user_data['printer']
    username = update.effective_user.username

    await context.bot.send_message(
        update.effective_chat.id,
        'Замена картриджа\n'
        f'Кабинет: {room}\n'
        f'Принтер: {printer}\n'
        f'Дата: {date}',
        reply_markup=ReplyKeyboardRemove()
    )

    await context.bot.send_chat_action(update.effective_message.chat_id, ChatAction.TYPING)
    # TODO сделать корутиной запись в таблицу
    last_date, elapsed = printers.change_cartridge(room, printer, date)
    print(f'[ЗАМЕНА] {username=} {room=} {printer=} {date=}')
    # logger.info(f'[ЗАМЕНА] {username=} {room=} {printer=} {date=}')

    await context.bot.send_message(
        update.effective_chat.id,
        f'Прошлая замена: {last_date}\n'
        f'Ресурс картриджа в месяцах: {elapsed}'
    )

    context.user_data.clear()

    return ConversationHandler.END


async def cartridge_incoming(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Первый этап из диалога по привозу картриджей: Этаж-Кабинет-Принтер-Дата-**Готово**.

    Регистрирует замену картриджа в Google-таблице и выдает сообщение о предыдущей замене.

    :return: Состояние ConversationHandler.END
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        'Я пока не умею регистрировать привоз картриджей, увы...',
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Прерывает любой из диалогов на любом этапе."""
    # TODO очистить словарь состояний
    await update.message.reply_text(
        'Ничего не делаем. Отмена',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
