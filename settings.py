"""
Здесь собираются настройки из файла settings.json
"""
import json


settings_file = 'key/settings.json'
with open(settings_file) as file:
    # Google-таблицы (их ключи)
    settings = json.load(file)


class Config:
    printers_gsheet_key = settings['PRINTERS_GSHEET_KEY']  # Реестр Принтеров
    macbook_gsheet_key = settings['MACBOOK_GSHEET_KEY']  # Реестр MacBook
    depo_gsheet_key = settings['DEPO_GSHEET_KEY']  # Реестр Depo
    lenovo_gsheet_key = settings['LENOVO_GSHEET_KEY']  # Реестр Lenovo
    technics_gsheet_key = settings['TECHNICS_GSHEET_KEY']  # Учет техники 1060
    scores_gsheet_key = settings['SCORES_GSHEET_KEY']  # Успеваемость (1 триместр) 2022-2023

    # Telegram-бот
    bot_token = settings['BOT_TOKEN']
    admin_ids = settings['ADMIN_IDS']

    echo_token = settings['ECHO_TOKEN']

    def __init__(self, **kwargs):
        pass


if __name__ == '__main__':
    print(Config.printers_gsheet_key)
    print(Config.admin_ids)
