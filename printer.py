"""
Класс Printer, который будет описывать объект принтера из Google-Таблицы "Реестр Принтеров"
"""


import datetime

import pygsheets
from settings import *


# Клиент - главный класс для работы с Google-документами. При создании происходит авторизация
client = pygsheets.authorize(service_file='key/python-waldorf-4f0f67808d79.json')


class Printer:
    table: pygsheets.spreadsheet
    sheets_list: list[pygsheets.worksheet]
    cartridge_sheet: pygsheets.worksheet
    summary_sheet: pygsheets.worksheet
    worksheet: pygsheets.worksheet

    CHANGE_COLUMN = 5  # Столбец с датами замен - Е (5)
    EVENT_COLUMN = 7  # Столбец с событиями - G (6)
    START_ROW = 5  # Первый ряд с данными (ряды 1-4 - заголовки)

    AUDITORY_CELL = 'A2'  # Кабинет
    MODEL_CELL = 'B2'  # Модель принтера
    CARTRIDGE_CELL = 'B4'  # Модель картриджа
    STATUS_CELL = 'B5'  # Состояние (Работает, Кончился картридж, Есть проблемы, В ремонте, Готов к выдаче
    NAME_CELL = 'B7'  # Сетевое имя принтера
    IP_ADDRESS_CELL = 'B8'  # IP-адрес принтера
    SERIAL_NUM_CELL = 'B10'  # Серийный № принтера
    INVENT_NUM_CELL = 'B11'  # Инвентарный № принтера
    NUM_CELL = 'B12'  # Внутренний № принтера

    def __init__(self, printer_sheet: pygsheets.worksheet):
        self.worksheet = printer_sheet
        self.room = printer_sheet.title[:3]
        self.name = printer_sheet.title[4:]

        self.last_change = None
        self.since_last_change = None
        self.last_row = None
        self.get_last_row()

    def get_last_row(self):
        """
        Обновляет значение свойств
            last_change - дата последней замены картриджа
            since_last_change - сколько прошло месяцев с последней замены
            last_row - номер последней заполненной строчки колонки <CHANGE_COLUMN>
        """
        days = [day for day in self.worksheet.get_col(self.CHANGE_COLUMN) if day]
        if self.last_row != len(days):
            self.last_row = len(days)
            self.last_change = days[-1]
            date_last = datetime.datetime.strptime(self.last_change, '%d.%m.%Y').date()
            date_before = datetime.datetime.strptime(days[-2], '%d.%m.%Y').date()
            self.since_last_change = (date_last - date_before).days / 30

    def change_cartridge(self, date: str | datetime.date) -> None:
        """
        Проставляет дату замены картриджа <date> на страницу принтера <room device>
        в первую пустую строчку колонки <CHANGE_COLUMN>

        :param date: str, дата замены в формате ДД.ММ.ГГГГ
        :return: tuple, предыдущая дата замены и количество месяцев, прошедших с этой даты
        """
        # last_row = self.get_last_row()
        if isinstance(date, datetime.date):
            date = date.strftime('%d.%m.%Y')

        self.worksheet.update_value((self.last_row + 1, self.CHANGE_COLUMN), date)

        self.last_change = self.worksheet.cell((self.last_row, self.CHANGE_COLUMN)).value
        self.since_last_change = self.worksheet.cell((self.last_row, self.CHANGE_COLUMN + 1)).value


# Открываем таблицу с помощью семейства методов open_<bla-bla-bla>
# table = client.open_by_key(PRINTERS_GSHEET_KEY)

# # Select worksheet by id, index, title.
# wks = sh.worksheet_by_title("my test sheet")
#
# # By any property
# wks = sh.worksheet('index', 0)
#
# # Get a list of all worksheets
# wks_list = sh.worksheets()
#
# # Or just
# wks = sh[0]

# sheet = table.worksheet_by_title('102 E120n')
# print(table.worksheets())
# print(sheet.url, sheet.title, sheet.index)
#
# sheet.update_value('E6', '30.01.2021')  # Записывает данные, как если бы пользователь вводил руками
# sheet.update_value('E7', '30.02.2021', parse=True)  # Записывает именно строчку


if __name__ == '__main__':

    printers = Printer()
    for item in printers.registry:
        print(item, printers.registry[item])
    buttons = [printer for printer in printers.registry['102']]
    printer_name, = printers.registry['102']
    print(buttons)

    sheet = printers.sheets_list[4]
    # column = sheet.get_col(printers.CHANGE_COLUMN)
    # start = printers.START_ROW - 1
    # for i in range(start, len(column)):
    #     print(column[i])
    #     if not column[i]:
    #         break
    # print(i + 1)
