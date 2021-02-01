import pygsheets
from settings import *


# Клиент - главный класс для работы с Google-документами. При создании происходит авторизация
client = pygsheets.authorize(service_file='key/python-waldorf-4f0f67808d79.json')


class Printers:
    def __init__(self):
        self.table = client.open_by_key(PRINTERS_GSHEET_KEY)
        self.sheets_list = self.table.worksheets()
        self.cartridge_sheet = self.sheets_list[0]  # Картриджи - лист 0
        self.summary_sheet = self.sheets_list[1]  # Summary - лист 1
        self.sheets_list = self.sheets_list[2:]

        self.registry = self.get_registry()

    def get_registry(self) -> dict:
        registry = {}
        for sheet in self.sheets_list:
            title = sheet.title
            room = title[:3]
            if room not in registry:
                registry[room] = {}
            printer = title[4:]
            registry[room][printer] = sheet
        return registry


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

# printers = Printers()
# for item in printers.registry:
#     print(item, printers.registry[item])
