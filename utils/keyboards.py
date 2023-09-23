"""
Модуль содержит функции, которые создают разные клавиатуры для Telegram-бота.
Используется библиотека python-telegram-bot версии 20.1
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def make_inline_keyboard(
        labels: list | tuple | dict,
        max_columns: int = 3,
        back_btn = None,
        cancel_btn = False
):
    """
    Создает Inline-клавиатуру из переданной коллекции.
    TODO расписать про текст клавиши и callback_data

    Args:
        labels: коллекция из строк или словарь вида строка: значение
        max_columns: максимальное число столбцов в клавиатуре
        back_btn:
        cancel_btn:

    Returns:
        instance of :class:`telegram.ext.InlineKeyboardMarkup`
    """
    # TODO предусмотреть случай, когда labels - это список списков
    if isinstance(labels, (list, tuple)):
        labels = {item: item for item in labels}
    buttons = [InlineKeyboardButton(text, callback_data=data) for text, data in labels.items()]

    if len(buttons) <= max_columns:
        return InlineKeyboardMarkup.from_row(buttons)

    # last_row = [InlineKeyboardButton('< Назад', callback_data=back_btn)] if back_btn
    # last_row += [InlineKeyboardButton('Отмена', callback_data='cancel') if cancel_btn]

    keyboard = [buttons[i:i+max_columns] for i in range(0, len(buttons), max_columns)]
    return InlineKeyboardMarkup(keyboard)


def make_reply_keyboard(
        buttons: list | tuple,
        max_columns: int = 3,
        resize_keyboard: bool = True,
        one_time_keyboard: bool = True,
        selective: bool = None,
        input_field_placeholder: str = None,
        is_persistent: bool = None,
):
    """
    Создает простую клавиатуру из переданной коллекции.

    :param buttons: коллекция из строк
    :param max_columns: максимальное число столбцов в клавиатуре
    :param one_time_keyboard: shadows the same parameter in :class:`telegram.ext.ReplyKeyboardMarkup`
    :param resize_keyboard: shadows the same parameter in :class:`telegram.ext.ReplyKeyboardMarkup`
    :param is_persistent: shadows the same parameter in :class:`telegram.ext.ReplyKeyboardMarkup`
    :param input_field_placeholder: shadows the same parameter in :class:`telegram.ext.ReplyKeyboardMarkup`
    :param selective: shadows the same parameter in :class:`telegram.ext.ReplyKeyboardMarkup`
    :return: Instance of :class:`telegram.ext.ReplyKeyboardMarkup`
    """
    # TODO предусмотреть случай, когда labels - это список списков
    keyboard = [buttons[i:i+max_columns] for i in range(0, len(buttons), max_columns)]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard,
        selective=selective,
        input_field_placeholder=input_field_placeholder,
        is_persistent=is_persistent,
    )


if __name__ == '__main__':
    make_inline_keyboard(['1', '2', '3', '4', '5', '6', '7'], 4)
