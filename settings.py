"""
Здесь собираются настройки из файла settings.json
"""
import json


settings_file = 'key/settings.json'
with open(settings_file) as file:
    # Google-таблицы (их ключи)
    settings = json.load(file)
    PRINTERS_GSHEET_KEY = settings['PRINTERS_GSHEET_KEY']  # Реестр Принтеров
    MACBOOK_GSHEET_KEY = settings['MACBOOK_GSHEET_KEY']  # Реестр MacBook
    DEPO_GSHEET_KEY = settings['DEPO_GSHEET_KEY']  # Реестр Depo
    LENOVO_GSHEET_KEY = settings['LENOVO_GSHEET_KEY']  # Реестр Lenovo
    TECHNICS_GSHEET_KEY = settings['TECHNICS_GSHEET_KEY']  # Учет техники 1060
    SCORES_GSHEET_KEY = settings['SCORES_GSHEET_KEY']  # Успеваемость (1 триместр) 2022-2023

    # Telegram-бот
    BOT_TOKEN = settings['BOT_TOKEN']
    ADMIN_IDS = settings['ADMIN_IDS']

    ECHO_TOKEN = settings['ECHO_TOKEN']


if __name__ == '__main__':
    print(PRINTERS_GSHEET_KEY)
    print(ADMIN_IDS)
