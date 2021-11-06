import pygsheets
from settings import *


# Клиент - главный класс для работы с Google-документами. При создании происходит авторизация
client = pygsheets.authorize(service_file='key/python-waldorf-4f0f67808d79.json')
template = client.open_by_key(SCORES_GSHEET_KEY)
# ToDo найти папку из свойств страницы. Использовать client.drive.
folder_id = '17yh08lEjH-cKy4XkEFRyIZkJJP_iImax'  # Admin 1060/Общие документы/2021-2022

CLASSES = [f'{grade}{letter}' for grade in '5678' for letter in 'ноп']
CLASSES += [f'{grade}{letter}' for grade in (9, 10, 11) for letter in 'но']


class Scores:
    template: pygsheets.spreadsheet
    table: pygsheets.spreadsheet
    folder_id: str
    sheet_to_be_kept: str

    _range: str = 'A1:AF55'
    _importrange_link = '=IMPORTRANGE("https://docs.google.com/spreadsheets/d/{}";"{}!{}")'

    def __init__(self, sheet_to_be_kept: str):
        self.template = template
        self.folder_id = folder_id
        self.sheet_to_be_kept = sheet_to_be_kept
        self.table = client.create(self.create_title(), self.template, self.folder_id)

        self.keep_one_sheet()
        self.link_to_template()
        self.table.share('', role='reader', type='anyone')

    def create_title(self) -> str:
        title = self.template.title
        grade = self.sheet_to_be_kept
        letter = grade[-1]
        new_letter = letter.capitalize()
        grade = grade.replace(letter, f' "{new_letter}"')
        new_title = title.replace('Успеваемость', f'{grade} Оценки')
        return new_title

    def keep_one_sheet(self) -> None:
        """
        Удаляет все листы таблицы, кроме той, что указана в атрибуте sheet_to_be_kept
        Очищает содержимое страницы и проставляет ссылку IMPORTRANGE на общую таблицу успеваемости
        """
        for grade in CLASSES:
            if grade != self.sheet_to_be_kept:
                sheet = self.table.worksheet_by_title(grade)
                self.table.del_worksheet(sheet)
        self.table.client.sheet.values_batch_clear(self.table.id, self._range)
        sheet = self.table.sheet1
        sheet.update_value('A1', self.link_to_template())

    def link_to_template(self) -> str:
        """
        Возвращает ссылку IMPORTRANGE на общую таблицу успеваемости
        """
        return self._importrange_link.format(self.template.id, self.sheet_to_be_kept, self._range)


if __name__ == '__main__':
    for grade in CLASSES:
        if grade in ('10н', '10о'):
            continue
        else:
            scores = Scores(grade)
            print(f'{grade}: {scores.table.url}')
            # ToDo сформировать письмо?
