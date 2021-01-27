import pygsheets


# Клиент - главный класс для работы с Google-документами. При создании происходит авторизация
client = pygsheets.authorize(service_file='key/python-waldorf-4f0f67808d79.json')

# Открываем таблицу с помощью семейства методов open_<bla-bla-bla>
table = client.open_by_key('1WeyL-_Eoj5UYAVyF6YjEbndDV8wXfg821iUA_R7C5YE')

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

sheet = table.worksheet_by_title('102 E120n')
print(table.worksheets())
print(sheet.url, sheet.title, sheet.index)
