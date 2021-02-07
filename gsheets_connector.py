import pygsheets
from settings import *


# Клиент - главный класс для работы с Google-документами. При создании происходит авторизация
client = pygsheets.authorize(service_file='key/python-waldorf-4f0f67808d79.json')


class Printers:
    table: pygsheets.spreadsheet
    sheets_list: list[pygsheets.worksheet]
    cartridge_sheet: pygsheets.worksheet
    summary_sheet: pygsheets.worksheet

    CHANGE_COLUMN = 5  # Столбец с датами замен - Е (5)
    EVENT_COLUMN = 7  # Столбец с событиями - G (6)
    START_ROW = 5  # Первый ряд с данными (ряды 1-4 - заголовки)

    def __init__(self):
        self.table = client.open_by_key(PRINTERS_GSHEET_KEY)
        self.sheets_list = self.table.worksheets()
        self.cartridge_sheet = self.sheets_list[0]  # Картриджи - лист 0
        self.summary_sheet = self.sheets_list[1]  # Summary - лист 1
        self.sheets_list = self.sheets_list[2:]

        self.registry = self.get_registry()

    def get_registry(self) -> dict[str, dict[str, pygsheets.worksheet]]:
        registry = {}
        for sheet in self.sheets_list:
            title = sheet.title
            room = title[:3]
            if room not in registry:
                registry[room] = {}
            printer = title[4:]
            registry[room][printer] = sheet
        return registry

    def change_cartridge(self, room: str, device: str, date: str) -> tuple[str, str]:
        """
        Проставляет дату замены картриджа <date> на страницу принтера <room device>
        в первую пустую строчку колонки <CHANGE_COLUMN>

        :param room: str, номер кабинета - ключ для соваря <registry>
        :param device: str, название принтера - ключ для словаря <registry[room]>
        :param date: str, дата замены в формате ДД.ММ.ГГГГ
        :return: tuple, предыдущая дата замены и количество месяцев, прошедших с этой даты
        """
        printer_sheet = self.registry[room][device]
        dates = [day for day in printer_sheet.get_col(self.CHANGE_COLUMN) if day]
        last_row = len(dates)
        printer_sheet.update_value((last_row + 1, self.CHANGE_COLUMN), date)

        last_date = printer_sheet.cell((last_row, self.CHANGE_COLUMN)).value
        elapsed = printer_sheet.cell((last_row, self.CHANGE_COLUMN + 1)).value
        return last_date, elapsed

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

    printers = Printers()
    # for item in printers.registry:
    #     print(item, printers.registry[item])

    sheet = printers.sheets_list[4]
    # column = sheet.get_col(printers.CHANGE_COLUMN)
    # start = printers.START_ROW - 1
    # for i in range(start, len(column)):
    #     print(column[i])
    #     if not column[i]:
    #         break
    # print(i + 1)
